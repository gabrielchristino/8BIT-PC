"""Host reference contract for complete keypad frames, not CPU firmware.

Static <=2-key admission relies on NET-17 electrical bounds. Sequential scans
are not simultaneous physical snapshots. No repeat or unrestricted NKRO.
"""
from collections import deque


class KeypadPolicy:
    def __init__(self,stable_frames=3,capacity=8):
        if stable_frames<2 or capacity<4:raise ValueError('Insufficient debounce or atomic-event capacity')
        self.stable_frames=stable_frames;self.capacity=capacity;self.events=deque()
        self.active=0;self.blocked=True;self.empty_frames=0
        self.last=None;self.count=0;self.overflows=0

    @staticmethod
    def admit_static(frame):
        if not isinstance(frame,int) or frame<0 or frame>=1<<64:raise ValueError('Expected a complete 64-bit frame')
        return frame if frame.bit_count()<=2 else None

    def cancel(self,reason):
        self.events.clear()
        self.events.extend([('CANCEL',reason),('ALL_UP',None)])
        self.active=0;self.blocked=True;self.empty_frames=0;self.last=None;self.count=0

    def update(self,frame):
        admitted=self.admit_static(frame)
        if admitted is None:
            if not self.blocked:self.cancel('more_than_two_keys')
            self.empty_frames=0
            return
        if self.blocked:
            self.empty_frames=self.empty_frames+1 if frame==0 else 0
            if self.empty_frames>=self.stable_frames:
                self.blocked=False;self.last=0;self.count=self.stable_frames
            return
        if frame!=self.last:self.last=frame;self.count=1
        else:self.count=min(self.count+1,self.stable_frames)
        if self.count<self.stable_frames or frame==self.active:return
        release=self.active & ~frame;press=frame & ~self.active
        events=[('RELEASE',k) for k in range(64) if release>>k&1]
        events += [('PRESS',k) for k in range(64) if press>>k&1]
        if len(self.events)+len(events)>self.capacity:
            self.overflows+=1;self.cancel('queue_overflow');return
        self.events.extend(events);self.active=frame

    def drain(self):
        events=list(self.events);self.events.clear();return events
