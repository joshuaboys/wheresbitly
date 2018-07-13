import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ServiceWorkerModule } from '@angular/service-worker';
import { environment } from '../environments/environment';
import { CameraComponent } from './camera/camera.component';
import { TwitterComponent } from './twitter/twitter.component';
import { PrivacyComponent } from './privacy/privacy.component';
import { WinnerComponent } from './winner/winner.component';
import { TimerComponent } from './timer/timer.component';
import { FormsModule } from '@angular/forms';
import { WebcamModule } from 'ngx-webcam';
import { SignalRService } from './signalr.service';
import { HttpClientModule } from '@angular/common/http';
import { MatInputModule, MatButtonModule, MatSnackBarModule } from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';


@NgModule({
  declarations: [
    AppComponent,
    CameraComponent,
    TwitterComponent,
    PrivacyComponent,
    WinnerComponent,
    TimerComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ServiceWorkerModule.register('/ngsw-worker.js', { enabled: environment.production }),
	FormsModule,
    WebcamModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule
  ],
  providers: [SignalRService],
  bootstrap: [AppComponent]
})
export class AppModule { }
