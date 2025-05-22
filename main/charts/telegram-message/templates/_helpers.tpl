{{- define "telegramm-message.name" -}}
telegramm-message
{{- end }}

{{- define "telegramm-message.fullname" -}}
{{ .Release.Name }}-telegramm-message
{{- end }}
