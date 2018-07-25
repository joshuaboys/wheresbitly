import { Component, OnInit } from '@angular/core';
import { Meta } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'shared',
    templateUrl: './shared.component.html',
    styleUrls: ['./shared.component.scss']
})
export class SharedComponent implements OnInit {

    public isLoading = true;
    public url: string;
    private id: string;

    constructor( private readonly route: ActivatedRoute, private readonly meta: Meta) {
        this.route.params.subscribe(params => this.id = params['id']);
    }

    async ngOnInit() {
        try {
            const shareUrl = {url:"http://todo"};//TODO:
            if (shareUrl) {
                this.url = shareUrl.url;

                // TODO: add more meta tags here
                this.meta.addTags([
                        { name: 'twitter:card', content: 'summary_large_image' },
                        { name: 'twitter:creator', content: 'Elliot Wood' },
                        { name: 'twitter:image', content: this.url },
                        { name: 'twitter:site', content: '@BitWhere' },                    
                        { name: 'twitter:title', content: 'Wheres Bitly -- 2018' },
                        { name: 'twitter:url', content: location.href },                    
                        { property: 'og:description', content: '' },
                        { property: 'og:image', content: this.url },
                        { property: 'og:image:type', content: 'image/gif' },
                        { property: 'og:image:width', content: '640' },
                        { property: 'og:image:height', content: '480' },
                        { property: 'og:url', content: location.href },
                        { property: 'og:title', content: 'Wheres Bitly -- 2018' }
                    ],
                    true);
            }
        } catch (e) {
            console.error(e);
        } finally {
            this.isLoading = false;
        }
    }
}