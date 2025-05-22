{{- define "db-service.name" -}}
db-service
{{- end }}

{{- define "db-service.fullname" -}}
{{ .Release.Name }}-db-service
{{- end }}
