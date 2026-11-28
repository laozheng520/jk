package com.fongmi.android.tv.event;

import com.fongmi.android.tv.bean.Vod;

import org.greenrobot.eventbus.EventBus;

public class RefreshEvent {

    private final Type type;
    private String path;
    private Vod vod;

    public static void config() {
        EventBus.getDefault().post(new RefreshEvent(Type.CONFIG));
    }

    public static void video() {
        EventBus.getDefault().post(new RefreshEvent(Type.VIDEO));
    }

    public static void history() {
        EventBus.getDefault().post(new RefreshEvent(Type.HISTORY));
    }

    public static void keep() {
        EventBus.getDefault().post(new RefreshEvent(Type.KEEP));
    }

    public static void size() {
        EventBus.getDefault().post(new RefreshEvent(Type.SIZE));
    }

    public static void wall() {
        EventBus.getDefault().post(new RefreshEvent(Type.WALL));
    }

    public static void live() {
        EventBus.getDefault().post(new RefreshEvent(Type.LIVE));
    }

    public static void detail() {
        EventBus.getDefault().post(new RefreshEvent(Type.DETAIL));
    }

    public static void player() {
        EventBus.getDefault().post(new RefreshEvent(Type.PLAYER));
    }

    public static void subtitle(String path) {
        EventBus.getDefault().post(new RefreshEvent(Type.SUBTITLE, path));
    }

    public static void danmaku(String path) {
        EventBus.getDefault().post(new RefreshEvent(Type.DANMAKU, path));
    }

    public static void vod(Vod vod) {
        EventBus.getDefault().post(new RefreshEvent(Type.VOD, vod));
    }

    private RefreshEvent(Type type) {
        this.type = type;
    }

    public RefreshEvent(Type type, String path) {
        this.type = type;
        this.path = path;
    }

    private RefreshEvent(Type type, Vod vod) {
        this.type = type;
        this.vod = vod;
    }

    public Type getType() {
        return type;
    }

    public String getPath() {
        return path;
    }

    public Vod getVod() {
        return vod;
    }

    public enum Type {
        CONFIG, VIDEO, HISTORY, KEEP, SIZE, WALL, LIVE, DETAIL, PLAYER, SUBTITLE, DANMAKU, VOD
    }
}
