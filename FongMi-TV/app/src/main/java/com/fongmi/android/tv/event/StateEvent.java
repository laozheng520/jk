package com.fongmi.android.tv.event;

import org.greenrobot.eventbus.EventBus;

public class StateEvent {

    private final Type type;

    public static void empty() {
        EventBus.getDefault().post(new StateEvent(Type.EMPTY));
    }

    public static void progress() {
        EventBus.getDefault().post(new StateEvent(Type.PROGRESS));
    }

    public static void content() {
        EventBus.getDefault().post(new StateEvent(Type.CONTENT));
    }

    private StateEvent(Type type) {
        this.type = type;
    }

    public Type getType() {
        return type;
    }

    public enum Type {
        EMPTY, PROGRESS, CONTENT
    }
}
