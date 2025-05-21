#!/bin/bash

echo "✅ بدء خطوات البناء المخصص..."

# حذف مكتبة websocket-client إن وجدت
pip uninstall -y websocket-client || echo "websocket-client غير مثبت"

# تثبيت الاعتمادات
pip install -r requirements.txt

echo "✅ البناء المخصص انتهى."
