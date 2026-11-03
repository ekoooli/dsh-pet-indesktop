# -*- coding: utf-8 -*-
"""macOS/Linux 混合 DPI 跨屏拖拽：跨窗映射走连续逻辑平面，不乘 DPR。

Windows 的每显示器 DPI 让 Qt 逻辑桌面不连续，必须用物理像素；macOS/Linux 的
全局坐标按点连续。此前两处共用物理公式，macOS 小屏 DPR 2 → 大屏 DPR 1 时源局部
被乘 2，拖拽域少掉近半块屏，实机表现是宠越拖越偏离鼠标、松手后错位。
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

import pet.overlay_shell as overlay_mod
from tests.test_overlay_hosts_multiscreen import (
    FakeScreen,
    _cleanup,
    _install_screens,
    _make_shell,
)

app = QApplication.instance() or QApplication([])


def _screens():
    """小屏（DPR 2，逻辑 1450×825）在左，大屏（DPR 1，逻辑 1900×1030）在右。"""
    small = FakeScreen((0, 0, 1450, 825), (0, 0, 1450, 825), dpr=2.0, name="SMALL")
    large = FakeScreen((1450, 0, 1900, 1030), (1450, 0, 1900, 1030), dpr=1.0, name="LARGE")
    return small, large


def _logical_plane_shell(tmp_path, monkeypatch):
    """强制非 Windows 映射平面，并让原点走逻辑坐标（在 Windows 上也确定）。"""
    monkeypatch.setattr(overlay_mod, "_IS_WINDOWS", False, raising=False)
    small, large = _screens()
    _install_screens(monkeypatch, small, large)
    shell = _make_shell(tmp_path, small, {"allow_cross_screen": True})
    # FakeScreen 没有原生窗口；Windows 的 GetWindowRect 分支在这里不适用。
    # 直接钉住逻辑原点，保证这条回归只测映射平面本身。
    monkeypatch.setattr(
        shell, "_window_physical_origin",
        lambda overlay: overlay.geometry().topLeft())
    return shell, small, large


def test_mixed_dpr_maps_in_the_logical_plane(tmp_path, monkeypatch):
    """小屏 DPR 2 → 大屏 DPR 1：目标局部 = 全局 - 目标原点，不乘 DPR。"""
    shell, small, large = _logical_plane_shell(tmp_path, monkeypatch)
    try:
        host_small = shell.host_for_screen(small)
        host_large = shell.host_for_screen(large)
        assert host_small is not host_large
        sprite = shell.sprite
        sprite.set_pos(QPointF(700, 600))

        mapped = shell._sprite_pos_in(sprite, host_small.overlay, host_large.overlay)
        assert mapped == QPointF(700 - 1450, 600), (
            "逻辑平面：小屏局部 700,600 = 全局 700,600 → 大屏局部 -750,600")
    finally:
        _cleanup(shell)


def test_negative_origin_layout_maps_without_dpr_scaling(tmp_path, monkeypatch):
    """用户实机布局：小屏 (0,33) DPR 2，大屏 (-204,-1050) DPR 1，向上拖。

    大屏在负原点/上方时，物理公式会把 y 除以 2，宠在拖到大屏上半段就被域钳住。
    """
    monkeypatch.setattr(overlay_mod, "_IS_WINDOWS", False, raising=False)
    small = FakeScreen((0, 33, 1450, 825), (0, 33, 1450, 825), dpr=2.0, name="SMALL")
    large = FakeScreen((-204, -1050, 1900, 1030), (-204, -1050, 1900, 1030),
                       dpr=1.0, name="LARGE")
    _install_screens(monkeypatch, small, large)
    shell = _make_shell(tmp_path, small, {"allow_cross_screen": True})
    monkeypatch.setattr(
        shell, "_window_physical_origin",
        lambda overlay: overlay.geometry().topLeft())
    try:
        host_small = shell.host_for_screen(small)
        host_large = shell.host_for_screen(large)
        sprite = shell.sprite
        shell._relax_drag_domain(sprite)  # 拖拽中才允许身体离开源屏
        sprite.set_pos(QPointF(700, -500))  # 已拖到小屏上方（大屏区域）

        mapped = shell._sprite_pos_in(sprite, host_small.overlay, host_large.overlay)
        # 全局 = (0,33)+(700,-500) = (700,-467)；大屏局部 = (700+204,-467+1050)
        assert mapped == QPointF(904, 583)

        domain = shell._drag_domain_local(host_small)
        assert domain is not None
        assert domain.left() <= -204, "拖拽域必须覆盖大屏左侧的负逻辑原点"
        assert domain.top() <= -1083, "拖拽域必须覆盖大屏上方（源局部负 y）"
    finally:
        _cleanup(shell)


def test_drag_domain_covers_the_large_screens_logical_extent(tmp_path, monkeypatch):
    """拖拽域必须覆盖大屏的逻辑右缘/下缘，不能被 DPR 乘小。

    旧公式把大屏右缘算成 (1450+1900)/2=1675，真实逻辑右缘是 3350：
    宠拖过大屏中段就跟不上鼠标（用户报的"鼠标偏移"）。
    """
    shell, small, large = _logical_plane_shell(tmp_path, monkeypatch)
    try:
        host_small = shell.host_for_screen(small)
        domain = shell._drag_domain_local(host_small)
        assert domain is not None
        assert domain.right() >= 3350 - 1, (
            f"拖拽域右缘 {domain.right()} 未覆盖大屏逻辑右缘 3350")
        assert domain.bottom() >= 1030 - 1, (
            f"拖拽域下缘 {domain.bottom()} 未覆盖大屏逻辑下缘 1030")
    finally:
        _cleanup(shell)


def test_release_hands_over_at_the_logical_body_center(tmp_path, monkeypatch):
    """松手归属按逻辑身体中心判定，交到目标窗后身体中心仍在同一逻辑坐标。"""
    shell, small, large = _logical_plane_shell(tmp_path, monkeypatch)
    try:
        host_small = shell.host_for_screen(small)
        host_large = shell.host_for_screen(large)
        sprite = shell.sprite
        # 拖拽中钳制域已放宽到全部屏；松手归属发生在这个状态下。
        shell._relax_drag_domain(sprite)
        body = sprite.body_rect()
        offset = QPointF(body.center()) - QPointF(sprite.pos)
        # 身体中心放在大屏内部（全局 1700,500），但宿主的窗还在小屏。
        sprite.set_pos(QPointF(1700, 500) - offset)
        assert shell.host_for_sprite(sprite) is host_small

        assert shell._place_sprite_in_physical_screen(sprite, persist=False) is True

        assert shell.host_for_sprite(sprite) is host_large, "按身体中心交到大屏窗"
        assert sprite.home_screen is large
        center = QPointF(sprite.body_rect().center())
        assert center.x() == pytest.approx(1700 - 1450)
        assert center.y() == pytest.approx(500)
    finally:
        _cleanup(shell)
