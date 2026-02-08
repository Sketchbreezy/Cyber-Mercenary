{{- /*
Expand the name of the chart.
*/ -}}
{{- $name := include "cyber-mercenary.name" . -}}
{{- /*
Create a default fully qualified app name.
*/ -}}
{{- $fullname := printf "%s-%s" $name .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- /*
Create chart name and version as used by the chart label.
*/ -}}
{{- $chart := printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- /*
Common labels
*/ -}}
{{- define "cyber-mercenary.labels" -}}
helm.sh/chart: {{ $chart }}
{{ include "cyber-mercenary.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: cyber-mercenary
{{- end -}}
{{- /*
Selector labels
*/ -}}
{{- define "cyber-mercenary.selectorLabels" -}}
app.kubernetes.io/name: {{ $name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
{{- /*
Create the name for the deployment.
*/ -}}
{{- define "cyber-mercenary.fullname" -}}
{{- $name := include "cyber-mercenary.name" . -}}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- /*
Create the name for the service account.
*/ -}}
{{- define "cyber-mercenary.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cyber-mercenary.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
