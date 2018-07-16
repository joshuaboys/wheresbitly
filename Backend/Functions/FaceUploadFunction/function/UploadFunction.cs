using System;
using System.Text;
using Microsoft.Azure;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;
using System.Diagnostics;
using System.IO;
using Microsoft.Azure.WebJobs;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;
using System.Collections.Generic;

namespace ServerlessRealtimeDemo
{
    public static class UploadFunction
    {

        [FunctionName("upload")]
        public static async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Anonymous, "get", "post")]HttpRequest req,
                                                    TraceWriter log, IBinder binder)
        {
            var files = req.Form.Files;
            if (files.Count == 0)
                return new NoContentResult();

            for (int i = 0; i < req.Form.Files.Count; i++)
            {
                var file = req.Form.Files[i];
                log.Info($"Upload to Blob: {file.FileName}");

                // Upload to the Blob Storage
                var guid = Guid.NewGuid();
                var path = $"images/{guid.ToString()}" + file.Name;
                var blobAttribute = new BlobAttribute(path, FileAccess.Write)
                {
                    Connection = "AzureStorageConnectionString"
                };

                using (var ms = new MemoryStream())
                {
                    file.CopyTo(ms);
                    var fileBytes = ms.ToArray();
                    // Save to blob storage
                    using (var writer = await binder.BindAsync<Stream>(blobAttribute))
                    {
                        await writer.WriteAsync(fileBytes, 0, fileBytes.Length);
                    }
                }
            }

            return new OkResult();
        }
    }
}
