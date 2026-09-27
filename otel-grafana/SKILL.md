---
name: otel-grafana
description: Instrumenta uma API .NET / ASP.NET Core com OpenTelemetry exportando os 3 sinais (métricas, traces e logs) via OTLP http/protobuf para Grafana (Prometheus/Loki/Tempo). Use quando o usuário pedir para "adicionar OpenTelemetry", "instrumentar a API", "mandar métricas/traces/logs para o Grafana", "configurar OTLP", ou quando um dashboard OTel estiver em "No data". Trigger: /otel-grafana
---

# Instrumentar API .NET com OpenTelemetry → Grafana (OTLP)

## Objetivo
Instrumentar uma API **ASP.NET Core (.NET 8+)** com OpenTelemetry, exportando os **três sinais** (métricas, traces e logs) via **OTLP `http/protobuf`** para o stack Grafana (Prometheus/Loki/Tempo). O dashboard filtra por `service.name`. Não acessar banco; não criar endpoints fictícios — as rotas vêm do roteamento real (controllers/minimal APIs) para o `http.route` ser preenchido automaticamente.

## ⚠️ Regra de ouro (a lição central desta skill)
**NÃO** dependa das variáveis de ambiente para definir endpoint/protocolo de cada sinal. Exportar via `AddOtlpExporter()` **sem argumentos** (lendo só as `OTEL_EXPORTER_OTLP_*`) é frágil: um override por-sinal no ambiente (`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_METRICS_EXPORTER`, etc.) ou o fallback pra **gRPC** faz **um sinal parar de chegar** enquanto os outros funcionam — sintoma clássico: "No data" só em parte do dashboard (ex.: métricas OK mas traces/logs não, ou vice-versa).

➡️ **Fixe `exporter.Endpoint` e `exporter.Protocol = HttpProtobuf` no código para os TRÊS sinais.** Use a env var apenas como *base* do endpoint (com fallback) e monte o path por-sinal (`/v1/traces`, `/v1/metrics`, `/v1/logs`) você mesmo.

## Pacotes NuGet
```
OpenTelemetry.Extensions.Hosting
OpenTelemetry.Instrumentation.AspNetCore
OpenTelemetry.Instrumentation.Http
OpenTelemetry.Exporter.OpenTelemetryProtocol
OpenTelemetry.Instrumentation.Runtime   # opcional (métricas de runtime/GC)
```

## Variáveis de ambiente (no systemd / container)
```
OTEL_EXPORTER_OTLP_ENDPOINT=https://SEU-ENDPOINT/otlp
OTEL_SERVICE_NAME=nome.da.sua.api
```
> O protocolo e o path por-sinal são fixados no código; a env define só a base do endpoint. Nada de credencial/endpoint hardcoded além do fallback.

## Código (Program.cs)
```csharp
using OpenTelemetry.Exporter;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var otelEnabled = builder.Configuration.GetValue("OpenTelemetry:Enabled", true);
if (otelEnabled)
{
    var serviceName = Environment.GetEnvironmentVariable("OTEL_SERVICE_NAME") ?? "nome.da.sua.api";
    var otlpBase = (Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT")
                    ?? "https://SEU-ENDPOINT/otlp").TrimEnd('/');

    builder.Services.AddOpenTelemetry()
        .ConfigureResource(r => r.AddService(serviceName))
        .WithTracing(t => t
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddOtlpExporter(e =>
            {
                e.Endpoint = new Uri($"{otlpBase}/v1/traces");
                e.Protocol = OtlpExportProtocol.HttpProtobuf;
            }))
        .WithMetrics(m => m
            .AddAspNetCoreInstrumentation()   // http.server.request.duration
            .AddHttpClientInstrumentation()
            .AddRuntimeInstrumentation()
            .AddOtlpExporter((e, reader) =>
            {
                e.Endpoint = new Uri($"{otlpBase}/v1/metrics");
                e.Protocol = OtlpExportProtocol.HttpProtobuf;
                reader.TemporalityPreference = MetricReaderTemporalityPreference.Cumulative; // Prometheus
                reader.PeriodicExportingMetricReaderOptions.ExportIntervalMilliseconds = 15000;
            }));

    builder.Logging.AddOpenTelemetry(l =>
    {
        l.IncludeScopes = true;
        l.IncludeFormattedMessage = true;
        l.SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(serviceName));
        l.AddOtlpExporter(e =>
        {
            e.Endpoint = new Uri($"{otlpBase}/v1/logs");
            e.Protocol = OtlpExportProtocol.HttpProtobuf;
        });
    });
}
```
> Registre o OpenTelemetry **fora** de `if (env.IsDevelopment())` para valer em produção. Não adicione middleware manual nem grave em banco. Se já houver logging em arquivo (ex.: NReco), **mantenha** — apenas adicione o `AddOpenTelemetry` ao pipeline de log.

## Como validar (NÃO confie no dashboard antes disso)
Siga nesta ordem — cada passo isola uma camada:

1. **Smoke test do endpoint** — deve retornar `200`/`400`, **nunca 404**:
   ```bash
   curl -i -X POST https://SEU-ENDPOINT/otlp/v1/metrics \
     -H "Content-Type: application/x-protobuf" --data-binary @/dev/null
   ```
   404 → problema de roteamento no nginx/collector (o `location /otlp/` precisa cobrir `/v1/*`), **não** no app.

2. **Isolar app vs pipeline** — envie uma métrica OTLP sintética (JSON) com o `service.name` da API para `/otlp/v1/metrics`:
   ```bash
   NOW=$(date +%s)000000000; START=$(( $(date +%s) - 60 ))000000000
   curl -s -o /dev/null -w "%{http_code}\n" -X POST https://SEU-ENDPOINT/otlp/v1/metrics \
     -H "Content-Type: application/json" --data-binary @- <<EOF
   {"resourceMetrics":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"nome.da.sua.api"}}]},
   "scopeMetrics":[{"metrics":[{"name":"probe_total","sum":{"aggregationTemporality":2,"isMonotonic":true,
   "dataPoints":[{"asInt":"42","startTimeUnixNano":"$START","timeUnixNano":"$NOW"}]}}]}]}]}
   EOF
   ```
   Se `probe_total` aparecer no Prometheus → pipeline OK; qualquer "No data" restante é do **app** (revise o código/env).

3. **Consultar o Prometheus direto** (via Grafana datasource proxy, usando a sessão logada):
   ```
   GET https://GRAFANA/grafana/api/datasources        # descobre o uid do Prometheus
   GET https://GRAFANA/grafana/api/datasources/proxy/uid/<uid>/api/v1/query?query=group by(__name__)({service_name="nome.da.sua.api"})
   ```
   Devem existir `http_server_request_duration_seconds_*`, `kestrel_*`, `http_client_*`.

4. **Gerar tráfego REAL** — use **https** e siga redirects (`curl -L`); `http://` costuma dar **301** e não chega no app. Rotas com auth retornam 401, mas ainda geram métrica com `http.route`.

## Gotchas de leitura do dashboard
- **"Taxa de Erro (5xx)" = No data** é correto quando não houve 5xx real (401/404 são 4xx).
- **req/s cai a 0** sem tráfego (é `rate()` sobre janela recente) — precisa de tráfego contínuo pra ver valores.
- **Métricas** levam ~15s (intervalo de export) + scrape; **traces** aparecem em segundos; **logs** quase imediato.
- Ajuste a janela do dashboard para **Last 15 minutes** + refresh, senão tráfego recente cai fora do intervalo visível.
- Se só UM sinal está em "No data" com os outros OK → é quase sempre a Regra de Ouro acima (endpoint/protocolo daquele sinal não fixado).

## Higiene de ambiente
Remova do serviço qualquer variável por-sinal conflitante (`OTEL_EXPORTER_OTLP_{TRACES,METRICS,LOGS}_ENDPOINT`, `OTEL_METRICS_EXPORTER`, etc.). O código já contorna fixando tudo, mas config divergente no ambiente é fonte de confusão futura.
