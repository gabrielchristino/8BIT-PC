def main():
    folder = ATTEMPT
    folder.mkdir(parents=True, exist_ok=True)
    base.OUT = folder
    base.MODELS = [('hardware/common_request/common_request_netlist.sv' if p=='hardware/system_access/system_access_netlist.sv' else ('hardware/local_phase_keyboard/local_phase_keyboard_netlist.sv' if p=='hardware/keyboard_500/keyboard_500_netlist.sv' else p)) for p in base.MODELS if p not in ('sim/net19a/isa1_memory_system.sv', 'sim/net14c/video_raster_async_netlist.sv')] + [
        'hardware/local_phase_reset/local_phase_reset_netlist.sv', 'sim/net23/clock_models.sv', 'sim/net26/isa1_memory_local_phase.sv', 'sim/net22/phase_packages.sv', 'sim/net25/warm_packages.sv', 'sim/net26/local_video_async.sv']
    original = base.fixture

    def fixture(text, timed, refs):
        text = original(text, timed, refs)
        text = text.replace('memory.raster.U8_0.recovery_events', 'memory.raster.U8.recovery_events').replace('memory.raster.U8_1.recovery_events', 'memory.raster.U8.setup_events')
        text = text.replace('stage1_recovery_events=', 'warm_recovery_events=').replace('stage2_recovery_events=', 'warm_setup_events=')
        old = 'dut(clk,reset_n,power_good,run,boot'
        if text.count(old) != 1:
            raise ValueError('Unexpected program CPU reset wiring')
        text = text.replace(old, "dut(memory.cpu_core_clk,memory.cpu_reset_n,1'b1,run,boot")
        text = text.replace('isa1_memory ', 'isa1_clocked_memory ')
        old = 'memory(clk,video_clk,reset_n,power_good,'
        assert text.count(old)==1
        text = text.replace(old, 'memory(reset_n,power_good,power_good,')
        old = 'reg clk=0,video_clk=0,reset_n=0,power_good=1,run=0;'
        assert text.count(old)==1
        text = text.replace(old, 'reg reset_n=0,power_good=1,run=0;\n wire clk=memory.cpu_source,video_clk=memory.master_source;')
        old = ' always #CPU_HALF clk=~clk;always #VIDEO_HALF video_clk=~video_clk;'
        assert text.count(old)==1
        text = text.replace(old, '')
        old = 'module tb_rtl_program;'
        assert text.count(old)==1
        text = text.replace(old, old+'\n defparam memory.reset_domains.CPU_PERIOD_NS=2*CPU_HALF, memory.reset_domains.MASTER_PERIOD_NS=2*VIDEO_HALF, memory.reset_domains.CPU_STARTUP_NS=10000000, memory.reset_domains.MASTER_STARTUP_NS=10000000;')
        progress="""
 integer next_progress=128;
 always @(posedge clk)begin
   #2000;
   if(n>=next_progress)begin
     $display("PROGRESS retired=%0d transactions=%0d simulated_ns=%0.3f PC=%h",n,transactions,$realtime,pc);
     $fflush();next_progress=next_progress+128;
   end
 end
"""
        text=once(text,'endmodule',progress+'endmodule')
        return text

    base.fixture = fixture
    sys.argv = [sys.argv[0], '--bench', 'program', '--timed']
    base.run = execute
    result = base.main()
    report_path = folder / 'system-program-timed.json'
    report = json.loads(report_path.read_text())
    report.update(scope='Full timed program at nominal100kHz CPU/25.175MHz master,10ms source startup, selected digital chip delays, initially unknown SRAM. Qualified oscillator VDD held valid. Binary warm/local reset boundary, not analog/PVT/jitter/MTBF/POR/PCB approval.',
                  supervisor_output_load_qualified=False)
    for name in ['tools/run_local_phase_program.py', 'tools/run_full_timed_program.py', 'tools/tracked_simulation.py', 'tools/prepare_local_phase_checks.py', 'tools/build_local_phase_reset.py', 'verification/net26/native/reset/local_phase_reset.xml', 'verification/net26/native/video/local_phase_video.xml', 'verification/net26/native/keyboard/local_phase_keyboard.xml', 'tools/build_common_request.py', 'verification/net24/native/common_request.xml']:
        report['sources'].append({'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest()})
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return result
