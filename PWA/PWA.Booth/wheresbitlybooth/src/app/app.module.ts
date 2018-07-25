import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MatInputModule, MatButtonModule, MatSnackBarModule } from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ServiceWorkerModule } from '@angular/service-worker';

// import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { environment } from '../environments/environment';

import { CameraComponent } from './camera/camera.component';
import { TwitterComponent } from './twitter/twitter.component';
import { PrivacyComponent } from './privacy/privacy.component';
import { WinnerComponent } from './winner/winner.component';
import { TimerComponent } from './timer/timer.component';
import { AudioComponent } from './audio/audio.component';
import { SignalRService } from './signalr.service';
import { FileUploadService } from './file-upload.service';
import { ControlWizardComponent } from './control-wizard/control-wizard.component';
import { SharedComponent } from './shared/shared.component';

@NgModule({
  declarations: [
    AppComponent,
    CameraComponent,
    TwitterComponent,
    PrivacyComponent,
    WinnerComponent,
    TimerComponent,
	ControlWizardComponent,
	AudioComponent,
    SharedComponent
  ],
  imports: [
    BrowserModule,
    // AppRoutingModule,
    RouterModule.forRoot([
		{ path: '', component: CameraComponent, pathMatch: 'full' },
            { path: 'images/:id', component: SharedComponent }
    ]),
    ServiceWorkerModule.register('/ngsw-worker.js', { enabled: environment.production }),
	FormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule
  ],
  providers: [
	SignalRService,
	FileUploadService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
