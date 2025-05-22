{{- define "telegram-message.name" -}}
telegram-message
{{- end }}

{{- define "telegram-message.fullname" -}}
{{ .Release.Name }}-telegram-message
{{- end }}
