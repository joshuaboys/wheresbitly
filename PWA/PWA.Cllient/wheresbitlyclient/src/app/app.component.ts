import { Component, OnInit } from '@angular/core';
import { SignalRService } from './signalr.service';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent implements OnInit {
  title = 'app';
  private readonly _signalRService: SignalRService;
  private readonly _snackBar: MatSnackBar;
  message: string;

  constructor(signalRService: SignalRService, snackBar: MatSnackBar) {
    this._signalRService = signalRService;
    this._snackBar = snackBar;
  }  

  ngOnInit() {
    this._signalRService.init();
    this._signalRService.messages.subscribe(message => {
      this._snackBar.open(message);
    });
  }

  send() {
    this._signalRService.send(this.message).subscribe(() => {});
  }
}
