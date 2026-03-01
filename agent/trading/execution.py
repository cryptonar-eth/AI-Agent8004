from __future__ import annotations
from agent.config.settings import Settings
from agent.core.proposals import Proposal, ProposalType
from agent.governance.approvals import is_approved
from agent.governance.policy import check_trade
from agent.ops.killswitch import is_killed
from agent.ops.audit import log

class Executor:
    def __init__(self, settings: Settings):
        self.settings = settings

    def execute(self, proposal: Proposal) -> None:
        if is_killed():
            log("blocked_killswitch", {"proposal_id": proposal.proposal_id, "type": proposal.type})
            print("[EXEC] BLOCKED: kill switch enabled")
            return

        if proposal.type == ProposalType.TRADE:
            symbol = str(proposal.payload.get("symbol"))
            side = str(proposal.payload.get("side"))
            qty = float(proposal.payload.get("qty"))

            ok, reason = check_trade(symbol, qty)
            if not ok:
                log("blocked_governance", {"proposal_id": proposal.proposal_id, "reason": reason, "payload": proposal.payload})
                print(f"[EXEC] BLOCKED: governance: {reason}")
                return

            if not self.settings.auto_execute_trades:
                if not is_approved(proposal.proposal_id):
                    log("blocked_no_approval", {"proposal_id": proposal.proposal_id, "payload": proposal.payload})
                    print(f"[EXEC] BLOCKED: not approved. Create approvals/{proposal.proposal_id}.approved")
                    return

            if self.settings.dry_run:
                log("dry_run_trade", {"proposal_id": proposal.proposal_id, "payload": proposal.payload, "reason": proposal.reason})
                print(f"[EXEC] DRY_RUN TRADE: {side} {qty} {symbol} :: {proposal.reason}")
                return

            # Live trading will be implemented later with a separate signer boundary.
            raise NotImplementedError("Live execution not implemented yet")

        log("blocked_unknown_type", {"proposal_id": proposal.proposal_id, "type": proposal.type})
        print(f"[EXEC] BLOCKED: unsupported proposal type: {proposal.type}")
