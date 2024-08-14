"""
Error Codes for all methods in the Attach service
"""
# update
iaas_attach_update_001 = (
    'The "resource_id" path parameter is invalid. "resource_id" does not correspond to a valid Resource in your '
    'Address.'
)
iaas_attach_update_002 = (
    'The "resource_id" path parameter is invalid. The Attach process is not supported for this Resource Type. Please'
    ' check the API docs to see the valid Resources that can be Attached.'
)
iaas_attach_update_003 = (
    'The "resource_id" path parameter is invalid. The Resource is already attached to another Resource.'
)
iaas_attach_update_004 = (
    'The "resource_id" path parameter is invalid. The Resource must be in the Running or Quiesced state in order to be'
    ' attached to another Resource.'
)
iaas_attach_update_005 = (
    'The "parent_resource_id" path parameter is invalid. "parent_resource_id" does not correspond to a valid '
    'Resource in your Address.'
)
iaas_attach_update_006 = (
    'The "resource_id" and "parent_resource_id" path parameters together are invalid. The Resource records that '
    'these correspond to belong to different Projects.'
)
iaas_attach_update_007 = (
    'The "parent_resource_id" path parameter is invalid. The Resource must be in the Running or Quiesced state in '
    'order to be attached to another Resource.'
)
iaas_attach_update_201 = (
    'You do not have permission to make this request. Robots cannot attach Resources.'
)
iaas_attach_update_202 = (
    'You do not have permission to make this request. A User must be public to attach Resources.'
)
