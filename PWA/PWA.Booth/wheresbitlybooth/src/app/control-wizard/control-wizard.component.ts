import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { clearInterval, setInterval } from 'timers';
import { AudioComponent } from '../audio/audio.component';
import { Routes, RouterModule } from '@angular/router';
export enum WizardState {
    Idle,
    CountingDown,
    TakingPhoto,
    PresentingPhotos,
    SendingPhoto,
    TextingLink
};

export interface PhotoDetails {
    photoCount: number;
    interval: number;
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

    public get isCountingDown(): boolean {
        return this.state === WizardState.CountingDown;
    }

    public get isTakingPhoto(): boolean {
        return this.state === WizardState.TakingPhoto;
    }

    public get isPresentingPhotos(): boolean {
        return this.state === WizardState.PresentingPhotos;
    }

    public get isTextingLink(): boolean {
        return this.state === WizardState.TextingLink;
    }

    public isSending = false;

    public state: WizardState = WizardState.Idle;
    public photoCountDown: number;
    public images: string[] = [];
    public animationIndex: number = 0;

    private countDownTimer: NodeJS.Timer;
    private animationTimer: NodeJS.Timer;

    private photosTaken: number = 0;

    async ngOnInit() {
        this.photoCountDown = 3;
    }

    private changeState(state: WizardState): void {
        console.log(`State: ${WizardState[state]}`);
        this.stateChange.emit(this.state = state);
    }

    public async start(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
        this.changeState(WizardState.CountingDown);
        this.resetCountDownTimer();
    }

    public async reset(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
        this.changeState(WizardState.Idle);
        this.photosTaken = 0;
        this.photoCountDown = 3;
        this.stopCountDownTimer();
        this.stopAnimationTimer();
    }

    public async generate(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
        if (this.images && this.images.length) {
            this.isSending = true;
			// TODO:
			window.location = "/images/0";

        }
    }

    public async send(sound: AudioComponent) {
        if (sound) {
            await sound.play();
        }
        this.changeState(WizardState.TextingLink);
    }
	private resetCountDownTimer(): void {
        this.stopCountDownTimer();
        this.startCountDownTimer();
    }
    private startCountDownTimer(): void {
		var timer = window.setInterval(() => {                  
			if (this.photosTaken < 3) {
				if (this.photoCountDown === 1) {
					this.photoCountDown = 3 + 1;
					this.changeState(WizardState.TakingPhoto);
					const details = {
						photoCount: this.photosTaken,
						interval: 3
					};
					this.takePhoto.emit(details);
					++ this.photosTaken;
				} else {
					this.changeState(WizardState.CountingDown);
					-- this.photoCountDown;
				}
			} else {
				this.stopCountDownTimer();
				this.images = [];
				for (var i = 0; i < 3; ++ i) {
					this.images.push(localStorage.getItem(`${i}.image.png`));
				}
				this.startAnimationTimer();
				this.changeState(WizardState.PresentingPhotos);
				this.photoCountDown = 3;
			}
        },1000);
        this.countDownTimer = timer;
    }

    private startAnimationTimer(): void {
        this.stopAnimationTimer();
		var timer = window.setInterval(() => {
                const index = (this.animationIndex + 1);
                if (index >= this.images.length) {
                    this.animationIndex = 0;
                } else {
                    this.animationIndex = index;
                }
            }, 1000);
        this.animationTimer = timer;
            
    }

    private stopAnimationTimer(): void {
        if (this.animationTimer) {
            window.clearInterval(this.animationTimer);
        }
    }

    private stopCountDownTimer(): void {
        this.images = [];
        if (this.countDownTimer) {
            window.clearInterval(this.countDownTimer);
        }
    }
}