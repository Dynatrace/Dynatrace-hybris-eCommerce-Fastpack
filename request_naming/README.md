# Global Request Naming Rules

* yBusinessProcessTask
  * for all transactions where the business process custom services are invoked, they are named by a combination of the task name and status
* yCronJobNameOnly
  * For all Cron Job custom services, the transactions are named by the specific Job name, without the numeric identifier. For instance, a cronjob service is by default named performCronJob. The yCronJobName request attribute captures a value like update-apparel-ukIndex-cronJob(8796112650741). This naming rule assigns the name update-apparel-ukIndex-cronJob to the transaction.
* yPageController
  * For all transactions containing the yPageController request attribute, the transaction is given the name of the specific page controller on the storefront service.
* yPlaceOrder
  * For request on the storefront that contain the yPlaceOrder request attribute, the transaction is given the name yPlace Order
