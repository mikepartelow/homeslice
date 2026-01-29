package lutron

import "testing"

func TestParseOutputLevel(t *testing.T) {
	level, ok := parseOutputLevel("~OUTPUT,2,1,100.00", 2)
	if !ok {
		t.Fatalf("expected ok")
	}
	if level != 100.00 {
		t.Fatalf("expected level 100.00 got %v", level)
	}

	level, ok = parseOutputLevel("~OUTPUT,2,1,0.00", 2)
	if !ok {
		t.Fatalf("expected ok")
	}
	if level != 0.00 {
		t.Fatalf("expected level 0.00 got %v", level)
	}

	_, ok = parseOutputLevel("~OUTPUT,3,1,0.00", 2)
	if ok {
		t.Fatalf("expected not ok for mismatched integration id")
	}
}
