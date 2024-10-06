package main

import (
	"fmt"
	"mp/gosonos/pkg/gosonos"
	"net"
)

func main() {
	a, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("192.168.1.204:%d", gosonos.PlayerPort)) // FIXME: awkward
	check(err)

	p := gosonos.Player{
		Address: a,
	}
	fmt.Println(p)

	tracks, err := p.Queue()
	check(err)
	for _, track := range tracks {
		fmt.Println(track.Id())
	}

	// bytes, err := os.ReadFile("ff.xml")
	// check(err)

	// dl := soap.DidlLite{}
	// err = dl.Unmarshal(bytes)
	// check(err)
	// for _, item := range dl.Items {
	// 	fmt.Println(strings.TrimSpace(item.Res.Value))
	// }

	fmt.Printf("%d tracks\n", len(tracks))
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
