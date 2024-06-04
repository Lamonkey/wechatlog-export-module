<script setup lang="ts">
import {defineProps, ref, onMounted, watch, nextTick, defineExpose} from "vue";
import http from '@/router/axios.js';
import MessageText from './MessageText.vue';
import MessageImg from './MessageImg.vue';
import MessageVideo from './MessageVideo.vue';
import MessageAudio from './MessageAudio.vue';
import MessageFile from './MessageFile.vue';
import MessageEmoji from './MessageEmoji.vue'
import MessageOther from "./MessageOther.vue";

interface User {
  account: string
  describe: string
  headImgUrl: string
  nickname: string
  remark: string
  wxid: string
  msg_count: number
}

interface UserList {
  [key: string]: User
}

interface msg {
  id: number
  type_name: string
  is_sender: number
  talker: string
  room_name: string
  content: {
    src: string
    msg: string
  }
  CreateTime: string
  MsgSvrID: string
}

// 这里的 props 是从父组件传递过来的
const props = defineProps({
  userData: {
    type: Object as () => User,
    required: true,
  },
  setScrollTop: {
    type: Function,
    required: true,
  },
  updateScrollTop: {
    type: Function,
    required: true,
  }
});


// 定义变量
const messages = ref<msg[]>([]);
const userlist = ref<UserList>({});
const msg_loading = ref(false);
const my_wxid = ref('');
const start = ref(0);
const limit = ref(100);
const msg_count = ref(0);
const hasScrolledToTop = ref(false);

// 获取聊天记录
const req_msgs = async (start: number, limit: number, wxid: string) => {
  if (msg_loading.value) {
    console.log("正在获取消息，请稍后再试!")
    return;
  }
  if (wxid == '') {
    console.log("wxid 为空, 请检查!")
    return;
  }
  try {
    msg_loading.value = true;
    if (start < 0) {
      start = 0;
    }
    // console.log('req_msgs', start, limit, wxid)
    const body_data = await http.post('/api/msgs', {
      'start': start,
      'limit': limit,
      'wxid': wxid,
    });
    messages.value = body_data.msg_list;
    userlist.value = Object.assign(userlist.value, body_data.user_list);
    msg_loading.value = false;
    return body_data;
  } catch (error) {
    msg_loading.value = false;
    console.error('Error fetching data:', error);
    return [];
  }
}
const req_msg_count = async (wxid: String) => {
  try {
    const body_data = await http.post('/api/msg_count', {
      'wxid': wxid,
    });
    return body_data[wxid];
  } catch (error) {
    console.error('Error fetching data msg_count:', error);
    return [];
  }
}
const get_my_wxid = async () => {
  try {
    const body_data = await http.get('/api/mywxid');
    return body_data.my_wxid;
  } catch (error) {
    console.error('Error fetching data my_wxid:', error);
    return [];
  }
}
// 上述为网络请求部分

// 初始加载数据
const fetchData = async () => {
  try {
    my_wxid.value = await get_my_wxid();
    msg_count.value = await req_msg_count(props.userData.wxid);
    start.value = msg_count.value - limit.value;
    if (start.value < 0) {
      start.value = 0;
    }
    await req_msgs(start.value, limit.value, props.userData.wxid);

    if (!hasScrolledToTop.value) {
      await nextTick(() => {
        props.setScrollTop();
        hasScrolledToTop.value = false;
      });
    }
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
};
// END 获取聊天记录

// 监听 userData 中 username 的变化
watch(() => props.userData.wxid, (newUsername, oldUsername) => {
  console.log('username changed： ', oldUsername, newUsername)
  messages.value = [];
  userlist.value = {};
  hasScrolledToTop.value = false;
  msg_count.value = 0;
  start.value = 0;

  fetchData();
});

//  循环请求获取全部数据
const loadMore = async () => {
  my_wxid.value = await get_my_wxid();
  msg_count.value = await req_msg_count(props.userData.wxid);

  let limit1 = limit.value;
  let start1 = start.value - limit1;
  if (start1 < 0) {
    start1 = 0;
  }
  const body_data = await req_msgs(start1, limit1, props.userData.wxid);
  start.value = start1;
  console.log('loadMore', start1,start.value, limit1, props.userData.wxid)
  messages.value = body_data.msg_list.concat(messages.value);
  // 排序
  messages.value.sort((a, b) => {
    return a.id - b.id;
  });
  // 去重
  messages.value = messages.value.filter((item, index, array) => {
    return index === 0 || item.id !== array[index - 1].id;
  });
  userlist.value = Object.assign(userlist.value, body_data.user_list);

  await nextTick(() => {
    props.updateScrollTop()
  })
};
defineExpose({
  loadMore
})

// 这部分为构造消息的发送时间和头像
const _direction = (msg: any) => {

  if (msg.talker == '我') {
    msg.talker = my_wxid.value;
  }
  const sendname = (msg) => {
    if (!userlist.value.hasOwnProperty(msg.talker)) {
      return msg.talker;
    }

    if (userlist.value[msg.talker].remark) {
      return userlist.value[msg.talker].remark;
    } else if (userlist.value[msg.talker].nickname) {
      return userlist.value[msg.talker].nickname;
    } else if (userlist.value[msg.talker].account) {
      return userlist.value[msg.talker].account;
    } else {
      return msg.talker;
    }
  }
  return `${sendname(msg)} [${msg.type_name}] ${msg.CreateTime}`;
}

const get_head_url = (msg: any) => {
  if (msg.talker == '我') {
    msg.talker = my_wxid.value;
  }
  if (!userlist.value.hasOwnProperty(msg.talker)) {
    return '';
  }
  return "/api/imgsrc/" + userlist.value[msg.talker].headImgUrl;
}

// END 这部分为构造消息的发送时间和头像


</script>

<template>
  <div id="chat">
    <div class="chat_body">
      <div class="chat_window" ref="chatWindow">
        <!--    加载更多    -->
        <div class="load_more" v-if="messages.length<msg_count"
             style="display: flex; justify-content: center; margin-top: 10px;margin-bottom: 10px;">
          <el-button type="primary" @click="loadMore">查看更多消息</el-button>
        </div>

        <div class="message" v-for="(msg,index) in messages" :key="index">
          <!-- 文字消息 -->
          <MessageText v-if="msg.type_name == '文本'" :is_sender="msg.is_sender" :direction="_direction(msg)"
                       :headUrl="get_head_url(msg)" :content="msg.content.msg"></MessageText>
          <!-- 图片消息 -->
          <MessageImg v-else-if="msg.type_name == '图片'" :is_sender="msg.is_sender" :direction="_direction(msg)"
                      :headUrl="get_head_url(msg)" :src="'/api/img/'+msg.content.src"></MessageImg>
          <!-- 表情消息 -->
          <MessageEmoji v-else-if="msg.type_name == '动画表情'" :is_sender="msg.is_sender" :direction="_direction(msg)"
                        :headUrl="get_head_url(msg)" :src="'/api/imgsrc/'+msg.content.src"></MessageEmoji>
          <!-- 视频消息 -->
          <MessageVideo v-else-if="msg.type_name == '视频'" :is_sender="msg.is_sender" :direction="_direction(msg)"
                        :headUrl="get_head_url(msg)" :src="'/api/video/'+msg.content.src"></MessageVideo>
          <!-- 文件消息 -->
          <MessageFile v-else-if="msg.type_name == '文件'" :is_sender="msg.is_sender" :direction="_direction(msg)"
                       :headUrl="get_head_url(msg)" :src="msg.content.src"></MessageFile>
          <!-- 语音消息 -->
          <MessageAudio v-else-if="msg.type_name == '语音'" :is_sender="msg.is_sender" :direction="_direction(msg)"
                        :headUrl="get_head_url(msg)" :src="'/api/'+msg.content.src"
                        :msg="msg.content.msg"></MessageAudio>
          <!-- 其他消息 -->
          <MessageOther v-else :is_sender="msg.is_sender" :direction="_direction(msg)" :headUrl="get_head_url(msg)"
                        :content="msg.content.msg"></MessageOther>

        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>

#chat {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;

  .chat_body {
    flex: 1;
    overflow-y: hidden;
    overflow-x: hidden;

    .chat_window {
      height: 100%;
      overflow-y: scroll;
      width: calc(100% + 17px);
      padding: 0px;
      margin: 0px;

      > .message:last-of-type {
        margin-bottom: 8px;
      }
    }
  }
}
</style>
