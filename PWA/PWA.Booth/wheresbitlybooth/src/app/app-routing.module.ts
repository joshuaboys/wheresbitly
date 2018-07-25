import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CameraComponent } from './camera/camera.component';
import { TimerComponent } from './timer/timer.component';
import { WinnerComponent } from './winner/winner.component';
import { PrivacyComponent } from './privacy/privacy.component';
import { TwitterComponent } from './twitter/twitter.component';

const routes: Routes = [
{ path: 'camera', component: CameraComponent }
  { path: 'camera', component: CameraComponent },
  { path: 'timer', component: TimerComponent },
  { path: 'winner', component: WinnerComponent },
  { path: 'privacy', component: WinnerComponent },
  { path: 'twitter', component: TwitterComponent },
];
 
@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule]
})
export class AppRoutingModule { }