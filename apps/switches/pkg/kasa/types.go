package kasa

type OnOff int

const (
	Off OnOff = 0
	On  OnOff = 1
)

type LightState struct {
	OnOff OnOff `json:"on_off"`
}

type SysInfoResponse struct {
	LightState LightState `json:"light_state"`
}

type SystemResponse struct {
	SysInfo *SysInfoResponse `json:"get_sysinfo,omitempty"`
}

type GenericResponse struct {
	System *SystemResponse `json:"system,omitempty"`
}

type GetSysinfoRequest struct {
}

type SetRelayStateRequest struct {
	State OnOff `json:"state"`
}

type SystemRequests struct {
	GetSysinfo    *GetSysinfoRequest    `json:"get_sysinfo,omitempty"`
	SetRelayState *SetRelayStateRequest `json:"set_relay_state,omitempty"`
}

type TransitionLightState struct {
	OnOff OnOff `json:"on_off"` // this can't be "omitempty" because 0 values, like on_off=0, are "empty"
}

type LightingService struct {
	TransitionLightState *TransitionLightState `json:"transition_light_state"`
}

type GenericRequest struct {
	System          *SystemRequests  `json:"system,omitempty"`
	LightingService *LightingService `json:"smartlife.iot.smartbulb.lightingservice,omitempty"`
}
