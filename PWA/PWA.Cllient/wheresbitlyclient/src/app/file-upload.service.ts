import { Injectable } from "@angular/core";
import { HttpClient, HttpEvent, HttpEventType, HttpProgressEvent, HttpRequest, HttpResponse, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Subject, Observable, throwError, of  } from 'rxjs';
import { catchError, retry, map, tap, last } from 'rxjs/operators';

@Injectable()
export class FileUploadService {

    private readonly _http: HttpClient;
    private readonly _baseUrl: string = "http://localhost:7071/api/";

    constructor(http: HttpClient) {
        this._http = http;
    }

    init() {
        console.log(`initializing FileUploadService...`);
    }
	
	public postFile(fileToUpload: File, requestUrl: string) {
		const formData: FormData = new FormData();
		formData.append('fileKey', fileToUpload, fileToUpload.name);
		
		let headers = new HttpHeaders();
        /** In Angular 5, including the header Content-Type can invalidate your request */
        headers.append('Content-Type', 'multipart/form-data');
        headers.append('Accept', 'application/json');
		
		const req = new HttpRequest('POST', requestUrl, formData, {
		  reportProgress: true,
		  headers: headers
		});
		
		return this._http.request(req)
		  .pipe(
			  map(e => this.getEventMessage(e, fileToUpload)),
			  tap(message => this.showProgress(message)),
			  last(), // return last (completed) message to caller
			  catchError(this.handleError(fileToUpload))
		  );
	}
	
	public postFileToUpload(fileToUpload: File) {
		return this.postFile(fileToUpload, this._baseUrl + "upload");
	}
	
	/** Return distinct message for sent, upload progress, & response events */
	private getEventMessage(e: HttpEvent<any>, file: File){
	  switch (e.type) {
		case HttpEventType.Sent:
		  return `Uploading file "${file.name}" of size ${file.size}.`;

		case HttpEventType.UploadProgress:
		  // Compute and show the % done:
		  const percentDone = Math.round(100 * e.loaded / e.total);
		  return `File "${file.name}" is ${percentDone}% uploaded.`;

		case HttpEventType.Response:
		  return `File "${file.name}" was completely uploaded!`;

		default:
		  return `File "${file.name}" surprising upload event: ${e.type}.`;
	  }
	}
	
	private handleError(file: File) {
    const userMessage = `${file.name} upload failed.`;

    return (error: HttpErrorResponse) => {
      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead
      const message = (error.error instanceof Error) ?
        error.error.message :
       `server returned code ${error.status} with body "${error.error}"`;

      console.log(`${userMessage} ${message}`);

      // Let app keep running but indicate failure.
      return of(userMessage);
    };
  }

  private showProgress(message: string) {
    console.log(message);
  }
}








