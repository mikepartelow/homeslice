package soap

import (
	"encoding/xml"
	"io"
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

	Xmlns string `xml:"xmlns,attr"`
	DC    string `xml:"xmlns:dc,attr"`
	UPnP  string `xml:"xmlns:upnp,attr"`
	R     string `xml:"xmlns:r,attr"`
}

type Item struct {
	XMLName xml.Name `xml:"item"`
	Id      string   `xml:"id,attr"`
	Desc    Desc     `xml:"desc"`
	Res     Res      `xml:"res,omitempty"`

	ParentID    string `xml:"parentID,attr"`
	Restricted  bool   `xml:"restricted,attr"`
	Title       string `xml:"dc:title"`
	Class       string `xml:"upnp:class"`
	Album       string `xml:"upnp:album"`
	Creator     string `xml:"dc:creator"`
	AlbumArtURI string `xml:"upnp:albumArtURI"`
	AlbumArtist string `xml:"r:albumArtist"`
}

type Desc struct {
	XMLName xml.Name `xml:"desc"`
	Value   string   `xml:",chardata"`

	ID        string `xml:"id,attr"`
	NameSpace string `xml:"nameSpace,attr"`
}

type Res struct {
	XMLName xml.Name `xml:"res"`
	Value   string   `xml:",chardata"`
}

func (d *DidlLite) Decode(r io.Reader) error {
	return xml.NewDecoder(r).Decode(d)

	// e := Envelope{}
	// if err := xml.NewDecoder(r).Decode(&e); err != nil {
	// 	return fmt.Errorf("error unmarshaling Envelope: %w", err)
	// }

	// if err := xml.Unmarshal([]byte(e.Body.BrowseResponse.Result), d); err != nil {
	// 	return fmt.Errorf("error unmarshaling Envelope.Body.BrowseResponse.Result: %w", err)
	// }

	// return nil
}

func (d *DidlLite) Encode(w io.Writer) error {
	return xml.NewEncoder(w).Encode(d)
}
