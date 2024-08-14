"""
Error Codes for all methods in the Detach service
"""
# update
iaas_detach_update_001 = (
    'The "resource_id" path parameter is invalid. "resource_id" does not correspond to a valid Resource in your '
    'Address.'
)
iaas_detach_update_002 = (
    'The "resource_id" path parameter is invalid. The Detach process is not supported for this Resource Type. Please'
    ' check the API docs to see the valid Resources that can be Detached.'
)
iaas_detach_update_003 = (
    'The "resource_id" path parameter is invalid. The requested Resource is not attached to another Resource.'
)
iaas_detach_update_004 = (
    'The "resource_id" path parameter is invalid. Robots can only detach Quiesced Resources.'
)
iaas_detach_update_005 = (
    'The "resource_id" path parameter is invalid. The resource must be Running in order to request Detaching.'
)
iaas_detach_update_006 = (
    'The "resource_id" path parameter is invalid. The resource\'s parent must be Running or Quiesced in order to '
    'request Detaching.'
)
iaas_detach_update_201 = (
    'You do not have permission to make this request. Robots cannot detach Resources in other regions.'
)
iaas_detach_update_202 = (
    'You do not have permission to make this request. A User must be public to detach Resources.'
)
