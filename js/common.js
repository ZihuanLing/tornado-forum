const tsessionid = this.$cookies.get("tsessionid");
let username = this.$cookies.get("nick_name");
const userId = this.$cookies.get("user_id");
const store = new Vuex.Store({
    state:{
        tsessionid,
        groupId:3,
        username,
        notLogin:false,
        userId
    },
    mutations:{
        showname(state){
            if(!state.username){
                // location.href = '../../login.html';
                state.notLogin = false
            }else{
                state.notLogin = true
            }
        }

    }
})


/**
 * 退出登录
 */
function logout(){
    console.log("is loging out.")
    this.$cookies.remove('tsessionid');
    this.$cookies.remove('nick_name');
    this.$cookies.remove('user_id');

    location.href="/";

}
