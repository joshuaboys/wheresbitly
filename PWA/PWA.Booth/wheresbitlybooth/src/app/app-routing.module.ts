import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SocialComponent } from './social/social.component';
import { TimerComponent } from './timer/timer.component';
import { WinnerComponent } from './winner/winner.component';

const routes: Routes = [
  { path: 'social', component: SocialComponent },
  { path: 'timer', component: TimerComponent },
  { path: 'winner', component: WinnerComponent },
];
 
@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule]
})
export class AppRoutingModule { }