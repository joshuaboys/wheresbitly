import { Component, Inject, ViewChild, OnInit, AfterViewInit, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { WizardState, PhotoDetails } from '../control-wizard/control-wizard.component';
import { setTimeout } from 'timers';
import { FileUploadService } from '../file-upload.service';

@Component({
    selector: 'camera',
    templateUrl: './camera.component.html',
    styleUrls: ['./camera.component.css']
})
export class CameraComponent implements AfterViewInit {
    @ViewChild('video') videoElement: ElementRef;
    private video: HTMLVideoElement;

    @ViewChild('canvas') canvasElement: ElementRef;
    private canvas: HTMLCanvasElement;

    public isPresentingPhotos = false;
    public isTextingLink = false;
    public isTakingPhoto = false;
    public imageWidth = 640;
    public imageHeight = 480;

	private readonly _fileUploadService : FileUploadService;
	  
	constructor(fileUploadService: FileUploadService) { 
		this._fileUploadService = fileUploadService;
	}
	
    ngAfterViewInit(): void {
        if (this.videoElement && this.videoElement.nativeElement) {
            this.video = this.videoElement.nativeElement as HTMLVideoElement;
            if (this.video) {
                this.getMediaStreamPromise({ video: true })
                    .then((stream: MediaStream) => this.video.srcObject = stream);

                this.video.height = window.innerHeight;
            }
        }
        if (this.canvasElement && this.canvasElement.nativeElement) {
            this.canvas = this.canvasElement.nativeElement as HTMLCanvasElement;
        }
    }

    private getMediaStreamPromise(constraints: MediaStreamConstraints): Promise<MediaStream> {
        if (navigator.mediaDevices.getUserMedia) {
            return navigator.mediaDevices.getUserMedia(constraints);
        }

        let getMediaStream = ((
                navigator['webkitGetUserMedia'] ||
                navigator['mozGetUserMedia']) as (c: MediaStreamConstraints) => Promise<MediaStream>
            ).bind(navigator);

        return getMediaStream(constraints);
    }

    public onTakePhoto(details: PhotoDetails): void {
        window.setTimeout(() => {
            if (this.canvas) {
                const context = this.canvas.getContext('2d');
                if (context) {
                    context.drawImage(this.video, 0, 0, this.imageWidth, this.imageHeight);
					
					var name = `${details.photoCount}.image.png`;
                    const url = this.canvas.toDataURL('image/png');
                    localStorage.setItem(name, url);
				
					var imageBlob = this.dataURItoBlob(url);
					var imageFile = this.blobToFile(imageBlob, name);
					
					this._fileUploadService.postFileToUpload(imageFile).subscribe(data => {
						console.log(data);
					}, error => {
						console.log(error);
					});
                }
            }
        }, details.interval / 2);
    }

    public onStateChanged(state: WizardState): void {
        this.isPresentingPhotos = state === WizardState.PresentingPhotos;
        this.isTextingLink = state === WizardState.TextingLink;
        this.isTakingPhoto = state === WizardState.TakingPhoto;
    }

    public adjustVideoHeight(event): void {
        if (event && this.video) {
            this.video.height = event.target.innerHeight;
        }
    }
	private dataURItoBlob(dataURI) {
		// convert base64 to raw binary data held in a string
		// doesn't handle URLEncoded DataURIs - see SO answer #6850276 for code that does this
		var byteString = atob(dataURI.split(',')[1]);

		// separate out the mime component
		var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

		// write the bytes of the string to an ArrayBuffer
		var ab = new ArrayBuffer(byteString.length);
		var ia = new Uint8Array(ab);
		for (var i = 0; i < byteString.length; i++) {
			ia[i] = byteString.charCodeAt(i);
		}

		//Old Code
		//write the ArrayBuffer to a blob, and you're done
		//var bb = new BlobBuilder();
		//bb.append(ab);
		//return bb.getBlob(mimeString);

		//New Code
		return new Blob([ab], {type: mimeString});

	}
	  
	private blobToFile = (theBlob: Blob, fileName:string): File => {
		var b: any = theBlob;
		//A Blob() is almost a File() - it's just missing the two properties below which we will add
		b.lastModifiedDate = new Date();
		b.name = fileName;
		
		//Cast to a File() type
		return <File>theBlob;
	}
}