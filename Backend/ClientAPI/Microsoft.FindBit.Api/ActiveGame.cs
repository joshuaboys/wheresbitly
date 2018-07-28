using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Azure.WebJobs.Host;

namespace Microsoft.FindBit.Api
{
    public static class ActiveGame
    {
        [FunctionName("ActiveGame")]
        public static IActionResult Run([HttpTrigger(AuthorizationLevel.Function, "get", Route = null)]HttpRequest req, TraceWriter log)
        {
            log.Info("C# HTTP trigger function processed a request.");

            // read Cosmos for active configuration.

            return new JsonResult(new GameConfiguration { GameLevel = 2, EventName = "DDD Perth", BitUrl = "https://whereisbitdev01.blob.core.windows.net/entries/6de7055f-20b5-4169-80f4-bdaec2a5265f.png" });           
        }
    }

    public class GameConfiguration
    {
        public int GameLevel { get; set; }
        public string EventName { get; set; }
        public string BitUrl { get; set; }
    }
}
