package main

import (
	"fmt"
	"mp/gosonos/pkg/sonos"
	"net"
)

func main() {
	// DR
	caddress, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("192.168.1.204:%d", sonos.PlayerPort)) // FIXME: awkward
	check(err)

	controller := sonos.Player{
		Addr: caddress,
	}

	// KCH
	paddress, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("192.168.1.169:%d", sonos.PlayerPort)) // FIXME: awkward
	check(err)

	p := sonos.Player{
		Addr: paddress,
	}

	err = controller.Play()
	check(err)

	err = p.Join(&controller)
	check(err)

	// trackIds := []gosonos.TrackId{
	// 	gosonos.TrackId("73569259"),
	// 	gosonos.TrackId("16334233"),
	// 	gosonos.TrackId("21702638"),
	// 	gosonos.TrackId("97874177"),
	// }

	// err = p.AddTracks(trackIds)
	// check(err)

	// tracks, err := p.Queue()
	// check(err)
	// for _, track := range tracks {
	// 	fmt.Println(track.Id())
	// }

	// bytes, err := os.ReadFile("ff.xml")
	// check(err)

	// dl := soap.DidlLite{}
	// err = dl.Unmarshal(bytes)
	// check(err)
	// for _, item := range dl.Items {
	// 	fmt.Println(strings.TrimSpace(item.Res.Value))
	// }

	// fmt.Printf("%d tracks\n", len(tracks))
}

func check(err error) {
	fmt.Println("FIXME")
	if err != nil {
		panic(err)
	}
}

// package main

// import (
//     "encoding/xml"
//     "fmt"
// )

// var data = `<?xml version="1.0"?>
// <GetAssignmentResponse>
//     <Answer>&lt;?xml version="1.0" encoding="UTF-8" standalone="no"?&gt;
//         &lt;QuestionFormAnswers xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd"&gt;
//         &lt;Answer&gt;
//         &lt;QuestionIdentifier&gt;Q1HasEvents&lt;/QuestionIdentifier&gt;
//         &lt;FreeText&gt;no&lt;/FreeText&gt;
//         &lt;/Answer&gt;
//         &lt;/QuestionFormAnswers&gt;
//     </Answer>
// </GetAssignmentResponse>`

// type Response struct {
//     XMLName xml.Name `xml:"GetAssignmentResponse"`
//     Answer  string   `xml:"Answer"`
// }

// type Answer struct {
//     XMLName  xml.Name `xml:"QuestionFormAnswers"`
//     FreeText string   `xml:"FreeText"`
// }

// func main() {
//     v := Response{}
//     err := xml.Unmarshal([]byte(data), &v)
//     if err != nil {
//         fmt.Printf("error: %v", err)
//         return
//     }
//     fmt.Printf("Answer = %q\n", v.Answer)
//     a := Answer{}
//     err = xml.Unmarshal([]byte(v.Answer), &a)
//     if err != nil {
//         fmt.Printf("error: %v", err)
//         return
//     }
//     fmt.Printf("Answer = %#v\n", a)
// }
