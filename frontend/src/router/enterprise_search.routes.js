import { Layout, upload, search } from '@/views/enterprise_search';

export default {
    path: '/enterprise_search',
    component: Layout,
    children: [
        { path: '', redirect: 'upload' },
        { path: 'upload', component: upload },
        { path: 'search', component: search }
    ]
};
