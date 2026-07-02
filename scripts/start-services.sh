#!/bin/bash
# pm-director service management via systemd --user
# Usage: bash scripts/start-services.sh [start|stop|restart|status|enable]
CMD="${1:-restart}"
case "$CMD" in
  start)    systemctl --user start pm-backend pm-frontend ;;
  stop)     systemctl --user stop pm-backend pm-frontend ;;
  restart)  systemctl --user restart pm-backend pm-frontend ;;
  enable)   systemctl --user enable pm-backend pm-frontend; loginctl enable-linger samuel ;;
  status)
    echo "=== Services ==="
    systemctl --user is-active pm-backend pm-frontend 2>/dev/null
    echo "=== Frontend ==="
    curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:5777/
    echo "=== Backend ==="
    curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:8800/api/stats
    ;;
  *) echo "Usage: $0 [start|stop|restart|status|enable]"; exit 1 ;;
esac
