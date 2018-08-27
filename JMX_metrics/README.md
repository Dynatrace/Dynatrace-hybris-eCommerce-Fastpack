# JMX Files for Import
All JMX zip files should be stored in the directory /JMX_metrics.

The files listed in /jmx_metrics.txt will be imported.

To add a file to /jmx_metrics.txt, please use the following format:
> JMX_metrics/\<metricgroup\>.zip

Only zip files can be uploaded in this way.
The name of the actual JMX plugin file contained in the zip file has to be
>plugin.json

Because of this limitaion in the name, you can only put one JSON file in a zip file. If you want use multiple metric groups:
* Name the first JSON file plugin.json.
* Zip the plugin.json file into a uniquely named ZIP file.
* Delete the original plugin.json file and repeat these steps for each unique XML metric group JSON file you want to upload.

**If a JMX plugin already exists with the same name, uploading will fail. To upload a new version, edit the plugin.json file in the zip file and increase the minor or major version.**
>  "version": "1.0",

## Requirements
* Dynatrace Environment with OneAgent Installed on target hosts
* Dynatrace Environment permissions to upload custom plugins
* Valid plugin command line API token.
  + Once generated, a plugin command API token is only valid for 23 days.
  + To generate a token, go to Settings > Monitored Technologies > Custom plugins and copy the token.

[//]: # (The following section is specific for the fastpack you are creating and should be edited accordingly)


## JMX Metics for Hybris
The JMX Metrics listed below will be imported in this fastpack. Make any desired changes before importing. You can edit the individual JSON files to modify the grouping or you remove a file reference from /jmx_metrics.txt to eliminate an entire grouping. Please remember to update this readme when modifying the JSON/ZIP files.

### yDatabase JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|[y]DB Connections NumPhysicalOpen|NumPhysicalOpen|avg|
|[y]DB Connections NumInUse|NumInUse|avg|
|[y]DB Connections MaxPhysicalOpen|MaxPhysicalOpen|avg|
|[y]DB Connections MaxInUse|MaxInUse|avg|
|[y]DB Connections MaxAllowedPhysicalOpen|MaxAllowedPhysicalOpen|avg|
|[y]DB Connections Active|Active|avg|

### yEntityRegionCache JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|[y]EntityRegion MaximumCacheSize|MaximumCacheSize|avg|
|[y]EntityRegion HitRatio|HitRatio|avg|
|[y]EntityRegion HitCount|HitCount|avg|
|[y]EntityRegion EvictionCount|EvictionCount|avg|
|[y]EntityRegion CurrentCacheSize|CurrentCacheSize|avg|
|[y]EntityRegion CacheFillRatio|CacheFillRatio|avg|

### yGlobalRequestProcessor JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|GlobalRequestProcessor requestCount|requestCount|sum|
|GlobalRequestProcessor processingTime (ms)|processingTime|sum|
|GlobalRequestProcessor maxTime (ms)|maxTime|max|
|GlobalRequestProcessor errorCount|errorCount|sum|
|GlobalRequestProcessor bytesSent|bytesSent|sum|
|GlobalRequestProcessor bytesReceived|bytesReceived|sum|

### yJSPMonitor JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|JSPMonitor jspReloadCount|jspReloadCount|sum|
|JSPMonitor jspCount|jspCount|sum|

### yManager JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|Manager sessionMaxAliveTime (ms)|sessionMaxAliveTime|max|
|Manager sessionCounter|sessionCounter|sum|
|Manager sessionAverageAliveTime (ms)|sessionAverageAliveTime|avg|
|Manager rejectedSessions|rejectedSessions|sum|
|Manager processingTime (ms) sum|processingTime|sum|
|Manager expiredSessions|expiredSessions|sum|
|Manager duplicates|duplicates|sum|
|Manager activeSessions|activeSessions|sum|

### yQueryRegionCache JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|[y]QueryRegion MaximumCacheSize|MaximumCacheSize|avg|
|[y]QueryRegion HitRatio|HitRatio|avg|
|[y]QueryRegion HitCount|HitCount|avg|
|[y]QueryRegion EvictionCount|EvictionCount|avg|
|[y]QueryRegion CurrentCacheSize|CurrentCacheSize|avg|
|[y]QueryRegion CacheFillRatio|CacheFillRatio|avg|

### yServlet JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|Servlet requestCount|requestCount|sum|
|Servlet processingTime (ms)|processingTime|sum|
|Servlet minTime (ms)|minTime|avg|
|Servlet maxTime (ms)|maxTime|avg|
|Servlet loadTime (ms)|loadTime|sum|
|Servlet errorCount|errorCount|sum|

### ySessions JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|[y]VirtualJDBC activeSessions|activeSessions|avg|
|[y]Storefront activeSessions|activeSessions|avg|
|[y]ReportCockpit activeSessions|activeSessions|avg|
|[y]Medias activeSessions|activeSessions|avg|
|[y]HMC activeSession|activeSessions|avg|
|[y]BackOffice activeSessions|activeSessions|avg|
|[y]AdminCockpit activeSession|activeSessions|avg|
|[y]AcceleratorServices activeSessions|activeSessions|avg|

### yTaskEngine JMX Metrics
The following table represents the the metrics in the current json file.


|Display name	|Metric source	|Aggregation|
|-------------|---------------|-----------|
|[y]TaskEngine queueSize|Count|avg|
|[y]TaskEngine executionTime 99thPercentile|99thPercentile|avg|
|[y]TaskEngine executionTime 75thPercentile|75thPercentile|avg|
|[y]TaskEngine executionTime 50thPercentile|50thPercentile|avg|


### Important links:

https://www.dynatrace.com/support/help/monitoring-plugins/application-plugins/how-do-i-monitor-jmx-metrics-in-my-java-applications/

 https://dynatrace.github.io/plugin-sdk/api/plugin_json_apidoc.html
