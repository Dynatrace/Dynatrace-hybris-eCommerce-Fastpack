# Request Attributes

The following request attributes are default for Hybirs
* yBusinessProcessEngineName
  * Captures the Name of the business process from de.hybris.platform.processengine.process.ProcessengineTaskRunner.runProcessTask
* yBusinessProcessEngineStatus
  * Captures the Status of the business process from de.hybris.platform.processengine.process.ProcessengineTaskRunner.runProcessTask
* yCronJobName
  * Captures the Cron Job name from de.hybris.platform.servicelayer.internal.jalo.ServicelayerJob.performCronJob
* yCronJobResult
  * Captures the Cron Job result from de.hybris.platform.servicelayer.internal.jalo.ServicelayerJob.performCronJob
* yCurrency
  * Captures the Currency code from de.hybris.platform.commercefacades.order.impl.DefaultCheckoutFacade.afterPlaceOrder which can be used to analyze revenue by currency
* yGetUser
  * captures the user ID from de.hybris.platform.core.model.order.AbstractOrderModel.getUser. In the near future, we should be able to use this value to tag user sessions instead of data from the web page.
* yNumberOfSearchResults
  * Captures the number of search results from org.apache.solr.client.solrj.SolrClient.query
* yOrderItemCount
  * Captures the higher number of Items ordered from either de.hybris.platform.commercefacades.order.impl.DefaultCheckoutFacade.placeOrder or de.hybris.platform.acceleratorfacades.order.impl.DefaultAcceleratorCheckoutFacade.placeOrder
* yOrderValue
  * captures the order value from de.hybris.platform.commercefacades.order.impl.DefaultCheckoutFacade.afterPlaceOrder. In the near future, we should be able to use this to track revenue on the Application as well as the current location - service layer.
* yPageController
  * Captures the page controller name from de.hybris.platform.acceleratorstorefrontcommons.controllers.AbstractController.addRequestToModel
* yPlaceOrder
  * Captures the invocation of de.hybris.platform.commercefacades.order.impl.DefaultCheckoutFacade.afterPlaceOrder for future use as a conversion rule. This method is invoked after the order is inserted into the order table in the database.
