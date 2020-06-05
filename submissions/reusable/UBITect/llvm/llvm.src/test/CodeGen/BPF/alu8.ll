; RUN: llc -march=bpfel -show-mc-encoding < %s | FileCheck %s

define i8 @mov(i8 %a, i8 %b) nounwind {
; CHECK-LABEL: mov:
; CHECK: r0 = r2 # encoding: [0xbf,0x20,0x00,0x00,0x00,0x00,0x00,0x00]
; CHECK: exit # encoding: [0x95,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
  ret i8 %b
}

define i8 @add(i8 %a, i8 %b) nounwind {
; CHECK-LABEL: add:
; CHECK: r0 = r1 # encoding: [0xbf,0x10,0x00,0x00,0x00,0x00,0x00,0x00]
; CHECK: r0 += r2 # encoding: [0x0f,0x20,0x00,0x00,0x00,0x00,0x00,0x00]
  %1 = add i8 %a, %b
  ret i8 %1
}

define i8 @and(i8 %a, i8 %b) nounwind {
; CHECK-LABEL: and:
; CHECK: r0 &= r2 # encoding: [0x5f,0x20,0x00,0x00,0x00,0x00,0x00,0x00]
  %1 = and i8 %a, %b
  ret i8 %1
}

define i8 @bis(i8 %a, i8 %b) nounwind {
; CHECK-LABEL: bis:
; CHECK: r0 |= r2 # encoding: [0x4f,0x20,0x00,0x00,0x00,0x00,0x00,0x00]
  %1 = or i8 %a, %b
  ret i8 %1
}

define i8 @xorand(i8 %a, i8 %b) nounwind {
; CHECK-LABEL: xorand:
; CHECK: r2 ^= -1 # encoding: [0xa7,0x02,0x00,0x00,0xff,0xff,0xff,0xff]
  %1 = xor i8 %b, -1
  %2 = and i8 %a, %1
  ret i8 %2
}

define i8 @xor(i8 %a, i8 %b) nounwind {
; CHECK-LABEL: xor:
; CHECK: r0 ^= r2 # encoding: [0xaf,0x20,0x00,0x00,0x00,0x00,0x00,0x00]
  %1 = xor i8 %a, %b
  ret i8 %1
}
