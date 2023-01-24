#!/usr/bin/env bash

session="mixboard"
main() {
    createSession
    separateScreens
    updateScreens
    connectSession
}

createSession() {
    tmux new -A -d -s $session
}

connectSession() {
    tmux ls
    tmux a -t $session
}

separateScreens() {
    tmux split-window -h bash
    tmux split-window -v bash
}

sendCommandToScreen() {
    tmux send -t "$session:0.$1" "$2" C-m
}

updateScreens() {
    updateScreenA &
    updateScreenB &
    updateScreenC
}

screenA() {
    sendCommandToScreen 0 "$1"
}

screenB() {
    sendCommandToScreen 1 "$1"
}

screenC() {
    sendCommandToScreen 2 "$1"
}

updateScreenB() {
    screenB "fuser -k 6379/tcp"
    screenB "redis-stack-server"
}

updateScreenA() {
    screenA "conda activate mixboard"
    screenA "celery --app handler.celery_app worker --concurrency=1"
}

updateScreenC ()
{
    screenC "conda activate mixboard"
    screenC "fuser -k 8000/tcp"
    screenC "gunicorn --workers=1 --bind=127.0.0.1 --timeout=120 -w 4 app:app"
}

main
