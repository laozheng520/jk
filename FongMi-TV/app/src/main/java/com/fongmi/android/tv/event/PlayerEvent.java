package com.fongmi.android.tv.event;

import org.greenrobot.eventbus.EventBus;

public class PlayerEvent {

    public static final int PREPARE = 0;
    public static final int PLAYING = 10;
    public static final int TRACK = 11;
    public static final int SIZE = 12;

    private final String tag;
    private final int state;

    public static void prepare(String tag) {
        EventBus.getDefault().post(new PlayerEvent(tag, PREPARE));
    }

    public static void playing(String tag) {
        EventBus.getDefault().post(new PlayerEvent(tag, PLAYING));
    }

    public static void track(String tag) {
        EventBus.getDefault().post(new PlayerEvent(tag, TRACK));
    }

    public static void size(String tag) {
        EventBus.getDefault().post(new PlayerEvent(tag, SIZE));
    }

    public static void state(String tag, int state) {
        EventBus.getDefault().post(new PlayerEvent(tag, state));
    }

    private PlayerEvent(String tag, int state) {
        this.state = state;
        this.tag = tag;
    }

    public String getTag() {
        return tag;
    }

    public int getState() {
        return state;
    }
}
