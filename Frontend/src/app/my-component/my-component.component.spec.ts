import { Component, OnInit } from '@angular/core';
import { DataService } from '../data.service';

@Component({
  selector: 'app-my-component',
  template: `
    <div *ngIf="data">
      {{ data.message }}
    </div>
  `,
  styleUrls: ['./my-component.component.css']
})
export class MyComponent implements OnInit {

  data: any;

  constructor(private dataService: DataService) { }

  ngOnInit(): void {
    this.dataService.getData().subscribe(response => {
      this.data = response;
    });
  }

}
