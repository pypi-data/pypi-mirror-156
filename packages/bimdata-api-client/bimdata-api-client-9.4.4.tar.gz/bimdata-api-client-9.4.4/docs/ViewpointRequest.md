# ViewpointRequest

Adds nested create feature

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int, none_type** |  | [optional] 
**guid** | **str** |  | [optional] 
**originating_system** | **str, none_type** | Name of the system in which the viewpoint is originated | [optional] 
**authoring_tool_id** | **str, none_type** | System specific identifier of the viewpoint in the originating BIM tool | [optional] 
**orthogonal_camera** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**perspective_camera** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**lines** | [**[LineRequest], none_type**](LineRequest.md) |  | [optional] 
**clipping_planes** | [**[ClippingPlaneRequest], none_type**](ClippingPlaneRequest.md) |  | [optional] 
**snapshot** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**components** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**pins** | [**[PinRequest], none_type**](PinRequest.md) | Non standard field. Pins (or markers/annotations) are points of interest | [optional] 
**temp_id** | **int, none_type** | Only used when using POST on the full-topic route to bind viewpoint with comment | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


