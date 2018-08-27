# Custom Services

The following custom services are default for Hybirs
* yBusinessProcessTask
  * Creates a custom service to capture executions of the Business Process Task starting with de.hybris.platform.processengine.process.ProcessengineTaskRunner.runProcessTask
* yCronJobs
  * Creates a custom service to capture the execution of Cron Jobs starting with de.hybris.platform.servicelayer.internal.jalo.ServicelayerJob.performCronJob.  If you execute cronjobs from other class/method combinations, you can add them here or through the Dynatrace interface after it is created.
* ySolrQuery
  * Creates a custom service to identify the Solr portion of they Hybris code as a micro-service within Hybris. This portion of the Hybris code is responsible for making calls to the backend Solr servers. Currently, there are 4 variations on the following method, with different arguments, that are instrumented, as different instances are used in different deployments: org.apache.solr.client.solrj.SolrClient.query
