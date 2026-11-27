"""Stage NET32 with the existing audited two-attempt exclusion policy."""
import runpy
from pathlib import Path

if __name__=='__main__':
    runpy.run_path(str(Path(__file__).with_name('stage_net31_review.py')),run_name='__main__')
