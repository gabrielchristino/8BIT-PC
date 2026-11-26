"""ISA-1 rev4.8: abstract synchronous release / asynchronous assertion reset model.
Not a gate-level or analog simulation. Python 3 standard library only.
"""
import json
from pathlib import Path

class ResetController:
    def __init__(self):
        self.ff1 = 0
        self.ff2 = 0
        self.pc = 0xBEEF
        self.fetch = False
        self.sram_we_n = 1
        self.eeprom_we_n = 1
        self.valid_clock_edges_while_reset = 0

    def assert_reset(self):
        # Model asynchronous assertion of supervisor-controlled reset.
        self.ff1 = self.ff2 = 0
        self.fetch = False
        self.sram_we_n = self.eeprom_we_n = 1
        self.valid_clock_edges_while_reset = 0

    def rising_edge(self, power_good, reset_button=False):
        if not power_good or reset_button:
            self.assert_reset()
            self.pc = 0  # synchronous /CLR of 74HC163 on this valid rising edge
            self.valid_clock_edges_while_reset += 1
            return
        old_ff1, old_ff2 = self.ff1, self.ff2
        self.ff1 = 1
        self.ff2 = old_ff1
        # On first edge after reset, ff2 stays 0 -> PC remains in reset.
        # On second edge, ff2 goes 1. Require prior reset edge to establish PC.
        if old_ff2 == 0:
            self.pc = 0
        self.fetch = bool(old_ff2 and self.valid_clock_edges_while_reset)
        self.sram_we_n = self.eeprom_we_n = 1


def test():
    checks = 0
    for start in range(65536):
        c = ResetController(); c.pc = start
        c.assert_reset()
        assert not c.fetch and c.sram_we_n and c.eeprom_we_n; checks += 3
        c.rising_edge(False)
        assert c.pc == 0 and not c.fetch; checks += 2
        c.rising_edge(True)
        assert not c.fetch and c.pc == 0; checks += 2
        c.rising_edge(True)
        assert not c.fetch and c.pc == 0; checks += 2
        c.rising_edge(True)
        assert c.fetch; checks += 1
        c.assert_reset()
        assert not c.fetch and c.sram_we_n and c.eeprom_we_n; checks += 3
    # A clock that never toggles cannot initialize a synchronous-clear PC.
    c = ResetController(); c.pc = 0x1234; c.assert_reset()
    assert c.pc == 0x1234 and not c.fetch; checks += 2
    # Safety: no valid edge during reset -> cannot fetch after release.
    for _ in range(10): c.rising_edge(True)
    assert not c.fetch; checks += 1
    # Brownout asserts reset without waiting for clock.
    c = ResetController(); c.valid_clock_edges_while_reset = 1
    for _ in range(3): c.rising_edge(True)
    assert c.fetch; checks += 1
    c.assert_reset(); assert not c.fetch; checks += 1
    result = {'revision':'4.8', 'assertions':checks, 'status':'PASS', 'scope':'abstract behavioral model only',
              'known_gap':'power-up clock validity, analog supply ramps, pin-level circuit, timing, reset sequencing hardware'}
    out = Path(__file__).with_name('isa1_rev48_results.json')
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__ == '__main__': test()
