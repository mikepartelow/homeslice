package kasa

type OnOff int

const (
	Off OnOff = 0
	on  OnOff = 1
)

type LightState struct {
	OnOff OnOff  `json:"on_off,omitempty"`
	Mode  string `json:"mode,omitempty"`
}

type SysInfoResponse struct {
	ErrCode    int        `json:"err_code,omitempty"`
	LightState LightState `json:"light_state,omitempty"`
	SwVer      string     `json:"sw_ver,omitempty"`
	HwVer      string     `json:"hw_ver,omitempty"`
	Type       string     `json:"type,omitempty"`
	Model      string     `json:"model,omitempty"`
	Mac        string     `json:"mac,omitempty"`
	DeviceID   string     `json:"deviceId,omitempty"`
	HwID       string     `json:"hwId,omitempty"`
	FwID       string     `json:"fwId,omitempty"`
	OemID      string     `json:"oemId,omitempty"`
	Alias      string     `json:"alias,omitempty"`
	DevName    string     `json:"dev_name,omitempty"`
	IconHash   string     `json:"icon_hash,omitempty"`
	RelayState int        `json:"relay_state,omitempty"`
	OnTime     int        `json:"on_time,omitempty"`
	ActiveMode string     `json:"active_mode,omitempty"`
	Feature    string     `json:"feature,omitempty"`
	Updating   int        `json:"updating,omitempty"`
	Rssi       int        `json:"rssi,omitempty"`
	LedOff     int        `json:"led_off,omitempty"`
	Latitude   int        `json:"latitude,omitempty"`
	Longitude  int        `json:"longitude,omitempty"`
	MicType    string     `json:"mic_type,omitempty"`
}

type SystemResponse struct {
	SysInfo *SysInfoResponse `json:"get_sysinfo,omitempty"`
}

type GenericResponse struct {
	System *SystemResponse `json:"system,omitempty"`
}

type GetSysinfoRequest struct {
}

type SystemRequests struct {
	GetSysinfo *GetSysinfoRequest `json:"get_sysinfo,omitempty"`
}

type GenericRequest struct {
	System *SystemRequests `json:"system,omitempty"`
}
