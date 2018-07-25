import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { clearInterval, setInterval } from 'timers';
import { AudioComponent } from '../audio/audio.component';
import { Routes, RouterModule } from '@angular/router';
import { SignalRService } from '../signalr.service';

export enum WizardState {
    Idle,
    NewGame,
	Timeout,
	TakePhoto,
	Send,
	Reset
};

export interface PhotoDetails {
    photoId: number;
};

@Component({
    selector: 'control-wizard',
    templateUrl: './control-wizard.component.html',
    styleUrls: ['./control-wizard.component.css']
})
export class ControlWizardComponent implements OnInit {
    @Output() takePhoto = new EventEmitter<PhotoDetails>();
    @Output() stateChange = new EventEmitter<WizardState>();
	
    public get isIdle(): boolean {
        return this.state === WizardState.Idle;
    }
    public get isNewGame(): boolean {
        return this.state === WizardState.NewGame;
    }
    public get isTimeout(): boolean {
        return this.state === WizardState.Timeout;
    }
	public get isTakePhoto(): boolean {
        return this.state === WizardState.TakePhoto;
    }
	public get isSend(): boolean {
        return this.state === WizardState.Send;
    }
	public get isReset(): boolean {
        return this.state === WizardState.Reset;
    }

    public state: WizardState = WizardState.Idle;

    public images: string[] = [];
	
    public findImage: string;
	private countDownTimer: NodeJS.Timer;
	
	// Set the date we're counting down to
	private countDownDate : number;
	private expireTimeString = "EXPIRED";

    constructor(private readonly signalRService: SignalRService) { 

	}

    async ngOnInit() {
		// TODO: GET THIS FROM SIGNALR
		// Get todays date and time
		var now = new Date().getTime();
		var minutes = 5;
		var future = new Date(now + minutes * 60000);
		this.countDownDate = future.getTime();
		this.resetCountDownTimer();
		this.changeState(WizardState.Idle);
    }
	
    private changeState(state: WizardState): void {
        console.log(`State: ${WizardState[state]}`);
        this.stateChange.emit(this.state = state);
    }

    public async start(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
		this.findImage = "../../assets/ccc-logo.png";

        this.changeState(WizardState.NewGame);
    }

    public async reset(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
        this.changeState(WizardState.Idle);
    }

    public async generate(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
		this.changeState(WizardState.TakePhoto);
		const details = {
			photoId: 1
		};
		this.takePhoto.emit(details);
		this.images = [];
		for (var i = 0; i < 3; ++ i) {
			this.images.push(localStorage.getItem(`${i}.image.png`));
		}
		this.changeState(WizardState.Send);
        if (this.images && this.images.length) {
    
			// TODO:
			//window.location.href = "/images/0";
        }
    }

    public async send(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
        this.changeState(WizardState.Send);
    }
	
	private startCountDownTimer(): void {
		var timer = window.setInterval(() => {

			// Get todays date and time
			var now = new Date().getTime();

			// Find the distance between now an the count down date
			var distance = this.countDownDate - now;
			
			// Time calculations for days, hours, minutes and seconds
			var days = Math.floor(distance / (1000 * 60 * 60 * 24));
			var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
			var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
			var seconds = Math.floor((distance % (1000 * 60)) / 1000);
			
			this.expireTimeString = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
  
			if (distance < 0){
				this.changeState(WizardState.Timeout);
				this.stopCountDownTimer();
			}
				
        },1000);
        this.countDownTimer = timer;
    }
	private stopCountDownTimer(): void {
        this.images = [];
        if (this.countDownTimer) {
            window.clearInterval(this.countDownTimer);
        }
    }
	private resetCountDownTimer(): void {
        this.stopCountDownTimer();
        this.startCountDownTimer();
    }
}