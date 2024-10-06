package soap

import (
	"encoding/xml"
	"fmt"
)

type Envelope struct {
	XMLName xml.Name `xml:"Envelope"`
	Body    Body     `xml:"Body"`
}

type Body struct {
	XMLName        xml.Name       `xml:"Body"`
	BrowseResponse BrowseResponse `xml:"BrowseResponse"`
}

type BrowseResponse struct {
	XMLName xml.Name `xml:"BrowseResponse"`
	Result  string   `xml:"Result"` // encoded XML, need to Unmarshal it separately
}

type DidlLite struct {
	XMLName xml.Name `xml:"DIDL-Lite"`
	Items   []Item   `xml:"item"`
}

type Item struct {
	XMLName xml.Name `xml:"item"`
	Res     Res      `xml:"res"`
}

type Res struct {
	XMLName xml.Name `xml:"res"`
	Value   string   `xml:",chardata"`
}

func (d *DidlLite) Unmarshal(bytes []byte) error {
	e := Envelope{}
	if err := xml.Unmarshal(bytes, &e); err != nil {
		return fmt.Errorf("error unmarshaling Envelope: %w", err)
	}

	if err := xml.Unmarshal([]byte(e.Body.BrowseResponse.Result), d); err != nil {
		return fmt.Errorf("error unmarshaling Envelope.Body.BrowseResponse.Result: %w", err)
	}

	return nil
}
