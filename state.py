"""
Constants for the different states in the CloudCIX system
"""

IN_API = -1
IGNORE = 0
REQUESTED = 1
BUILDING = 2
UNRESOURCED = 3
RUNNING = 4
QUIESCE = 5
QUIESCED = 6
RESTART = 7
SCRUB = 8
SCRUB_QUEUE = 9
RUNNING_UPDATE = 10
RUNNING_UPDATING = 11
QUIESCING = 12
RESTARTING = 13
SCRUB_PREP = 14
QUIESCED_UPDATE = 15
QUIESCED_UPDATING = 16
SCRUBBING = 17
CLOSED = 99

VALID_RANGE = [*range(IGNORE, SCRUBBING + 1), CLOSED]

ROBOT_STATE_MAP = {
    REQUESTED: {BUILDING, UNRESOURCED},
    BUILDING: {UNRESOURCED, RUNNING},
    UNRESOURCED: {REQUESTED, QUIESCE, RESTART, SCRUB, RUNNING_UPDATE, QUIESCED_UPDATE},
    QUIESCE: {QUIESCING},
    RESTART: {RESTARTING},
    SCRUB: {SCRUB_PREP, SCRUBBING},
    RUNNING_UPDATE: {RUNNING_UPDATING},
    RUNNING_UPDATING: {UNRESOURCED, RUNNING},
    QUIESCED_UPDATE: {QUIESCED_UPDATING},
    QUIESCED_UPDATING: {UNRESOURCED, QUIESCED},
    QUIESCING: {UNRESOURCED, QUIESCED},
    RESTARTING: {UNRESOURCED, RUNNING},
    SCRUB_PREP: {UNRESOURCED, SCRUB_QUEUE},
    SCRUB_QUEUE: {SCRUBBING},
    SCRUBBING: {UNRESOURCED, CLOSED},
}

USER_STATE_MAP = {
    RUNNING: {QUIESCE, SCRUB, RUNNING_UPDATE},
    QUIESCED: {RESTART, SCRUB, QUIESCED_UPDATE},
    SCRUB_QUEUE: {RESTART},
}

USER_SNAPSHOT_STATE_MAP = {
    RUNNING: {RUNNING_UPDATE, SCRUB},
}

USER_BACKUP_STATE_MAP = {
    RUNNING: {RUNNING_UPDATE, SCRUB},
}

# List of stable states a VM can be restored to when a Project is restored
VM_RESTORE_STATES = [
    RUNNING,
    QUIESCED,
]

# Map showing what states to restore a VM to from the last stable state the VM was in when a Project is restored
VM_RESTORE_MAP = {
    RUNNING: RESTART,
    QUIESCED: QUIESCED,
}

ROBOT_PROCESS_STATES = {
    REQUESTED,
    QUIESCE,
    RUNNING_UPDATE,
    QUIESCED_UPDATE,
    RESTART,
    SCRUB,
    SCRUB_QUEUE,
}

# Stable States
STABLE_STATES = [
    RUNNING,
    QUIESCED,
    SCRUB_QUEUE,
    CLOSED,
]

# BOM Create States - Set of states for which we should create new BOM entries
BOM_CREATE_STATES = {
    REQUESTED,
    RUNNING_UPDATE,
    QUIESCED_UPDATE,
    SCRUB,
    # Billing should resume if a VM is requested to restore from the SCRUB_QUEUE
    RESTART,
    QUIESCED,
}

# Billing Ignore States - set of states where we should set SKUs to 0
# Must be a subset of BOM_CREATE_STATES to work properly
BILLING_IGNORE_STATES = {
    SCRUB,
}

# States customer can request that may require and email to be sent by robot
SEND_EMAIL_STATES = [
    REQUESTED,
    QUIESCE,
    RESTART,
    SCRUB,
    RUNNING_UPDATE,
    QUIESCED_UPDATE,
]

# States that the scrub time for objs needs to be calculated based on the projects grace period
SCRUB_STATES = [
    SCRUB,
    SCRUB_PREP,
    SCRUB_QUEUE,
    SCRUBBING,
]
