/*import Cookies from 'https://cdn.jsdelivr.net/npm/js-cookie@3.0.1/dist/js.cookie.min.js'
Cookies.set('test', 7);*/
import {createApp} from 'https://unpkg.com/vue@3.2.33/dist/vue.esm-browser.js'
import {debounce} from 'https://cdn.jsdelivr.net/npm/lodash-es/+esm'

var app = createApp({
    data() {
        return {
            input_stand: getCookie('stand'),
            input_gpa: getCookie('gpa'),
            input_radio: this.set_radio(),
            input_college: getCookie('college'),
            table: undefined,
            college: null,
            input_email: getCookie('email'),
            input_text: undefined
        }
    },
    async created() {
        await this.get()
        this.get_college()
    },
    watch: {
        input_stand: 'input_change',
        input_gpa: 'input_change',
        input_college: 'college_change'
    },
    computed: {
        stand_ex(){
            if (this.input_radio == 'sat') {return '1410'}
            else if (this.input_radio == 'act') {return '30'}
            else {return ''}
        }
    },
    methods: {
        set_radio() {
            if (getCookie('radio') == ''){
                set_cookie('radio', 'sat')
            }
            return getCookie('radio')
        },
        update_stand: debounce(function (e) {
            this.input_stand = e.target.value
        }, 0),//500
        update_gpa: debounce(function (e) {
            this.input_gpa = e.target.value
        }, 0),//500
        update_radio: debounce(function (e) {
            //Note that the process for updating radio is different from stand
            //and GPA since there is no radio listener so all changes are with
            //this function only
            this.input_radio = e.target.value
            this.input_stand = undefined
            this.input_change()
        }, 0),//100
        update_college (e){
            this.input_college = e.target.value
        },
        /*get_cookies(){
            this.sat = getCookie('sat')
            this.gpa = getCookie('gpa')
            this.college = getCookie('college')
        },*/
        set_cookies(){
            set_cookie('stand', this.input_stand)
            set_cookie('gpa', this.input_gpa)
            set_cookie('radio', this.input_radio)
            set_cookie('college', this.input_college)
        },
        async get(){
            this.table = await (await fetch('api')).json()
            await this.get_college()
            /*this.update_pops()*/
        },
        input_change() {
            this.set_cookies()
            this.get()
        },
        async update_pops (){
            var popoverTriggerList = await [].slice.call(await document.querySelectorAll('.pop'))//[data-bs-toggle="popover"]
            var popoverList = await popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl)
            })
        },
        color(obj) {
            if (!obj || obj.color == null || obj.color == undefined) {return null}
            else{return 'color:hsla(' + obj.color + ',100%, 29.6%,1);'}
        },
        async get_college(){
            const delay = millis => new Promise((resolve, reject) => {
                setTimeout(_ => resolve(), millis)
            });
            let cookie = await getCookie('college')
            this.college = await this.table.find(
                function(element) {return element.name == cookie}
            )
            await delay(100)
            await this.update_pops()
        },
        async college_change() {
            await this.set_cookies()
            await this.get_college()
        },
        contact() {
            console.log('email: '+this.input_email+' text: '+this.input_text)
            set_cookie('email', this.input_email)
            fetch('contact', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: this.input_email,
                    text: this.input_text})
            })
            this.input_text = undefined
        },
        visibility(bool) {
            if (bool) {return 'visible'}
            else {return 'hidden' }
        }
    },
    delimiters: ['[[',']]']
}).mount('body')

//WW3 schools
function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function set_cookie(key, value) {
    document.cookie = key + "=" + value + "; expires=Fri, 31 Dec 9999 23:59:59 GMT; SameSite=Strict"
}
