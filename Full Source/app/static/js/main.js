/**
 * 위튜브 메인 JavaScript 파일
 * 공통 기능 및 유틸리티 함수를 포함합니다.
 */

// DOM 로드 완료 후 실행
document.addEventListener('DOMContentLoaded', function() {
    // 다크 모드 초기화
    initDarkMode();
    
    // 플래시 메시지 자동 닫기
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000); // 5초 후 자동으로 사라짐
    });
    
    // 프로필 이미지 미리보기
    const profileImageInput = document.getElementById('profile_image');
    if (profileImageInput) {
        profileImageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // 파일 크기 검증 (5MB 제한)
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    alert('이미지 파일 크기는 5MB 이하여야 합니다.');
                    e.target.value = '';
                    return;
                }
                
                // 파일 형식 검증
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('지원하지 않는 이미지 형식입니다. (jpg, jpeg, png, gif, webp만 가능)');
                    e.target.value = '';
                    return;
                }
                
                // FileReader를 사용하여 이미지 미리보기
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewImg = document.getElementById('profile-image-preview');
                    const placeholder = document.getElementById('profile-image-placeholder');
                    
                    if (previewImg) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block';
                    } else if (placeholder) {
                        // placeholder를 이미지로 교체
                        const img = document.createElement('img');
                        img.id = 'profile-image-preview';
                        img.src = e.target.result;
                        img.alt = '프로필 이미지';
                        img.style.width = '150px';
                        img.style.height = '150px';
                        img.style.borderRadius = '50%';
                        img.style.objectFit = 'cover';
                        placeholder.parentNode.replaceChild(img, placeholder);
                    } else {
                        // 새로운 이미지 요소 생성
                        const img = document.createElement('img');
                        img.id = 'profile-image-preview';
                        img.src = e.target.result;
                        img.alt = '프로필 이미지';
                        img.style.width = '150px';
                        img.style.height = '150px';
                        img.style.borderRadius = '50%';
                        img.style.objectFit = 'cover';
                        
                        const previewContainer = document.querySelector('.profile-image-preview');
                        if (previewContainer) {
                            previewContainer.innerHTML = '';
                            previewContainer.appendChild(img);
                        }
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

/**
 * 폼 유효성 검사 헬퍼 함수
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

/**
 * CSRF 토큰 가져오기
 */
function getCSRFToken() {
    // 메타 태그에서 CSRF 토큰 가져오기
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    // 쿠키에서 CSRF 토큰 가져오기 (Flask-WTF 기본 방식)
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}

/**
 * 비동기 요청 헬퍼 함수 (CSRF 토큰 자동 포함)
 */
async function fetchData(url, options = {}) {
    try {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // POST, PUT, DELETE 요청 시 CSRF 토큰 추가
        if (options.method && ['POST', 'PUT', 'DELETE'].includes(options.method.toUpperCase())) {
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
        }
        
        const response = await fetch(url, {
            headers: headers,
            credentials: 'same-origin',  // 쿠키 포함
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

/**
 * 댓글 수정 폼 표시 (버튼에서 호출)
 */
function editCommentFromButton(button) {
    const commentId = button.getAttribute('data-comment-id');
    const currentContent = button.getAttribute('data-comment-content');
    editComment(commentId, currentContent);
}

/**
 * 댓글 수정 폼 표시
 */
function editComment(commentId, currentContent) {
    // 모든 수정 폼 숨기기
    const allEditForms = document.querySelectorAll('.comment-edit-form');
    allEditForms.forEach(function(form) {
        form.style.display = 'none';
    });
    
    // 모든 댓글 텍스트 영역 다시 표시
    const allCommentTexts = document.querySelectorAll('.comment-text');
    allCommentTexts.forEach(function(text) {
        text.style.display = 'block';
    });
    
    // 해당 댓글의 수정 폼 표시
    const editForm = document.getElementById('edit-form-' + commentId);
    const editTextarea = document.getElementById('edit-content-' + commentId);
    
    if (editForm && editTextarea) {
        editForm.style.display = 'block';
        editTextarea.value = currentContent;
        editTextarea.focus();
        
        // 댓글 텍스트 영역 숨기기
        const commentText = editForm.previousElementSibling.previousElementSibling;
        if (commentText && commentText.classList.contains('comment-text')) {
            commentText.style.display = 'none';
        }
    }
}

/**
 * 댓글 수정 취소
 */
function cancelEdit(commentId) {
    const editForm = document.getElementById('edit-form-' + commentId);
    if (editForm) {
        editForm.style.display = 'none';
        
        // 댓글 텍스트 영역 다시 표시
        const commentText = editForm.previousElementSibling;
        if (commentText && commentText.classList.contains('comment-text')) {
            commentText.style.display = 'block';
        }
    }
}

/**
 * 대댓글 작성 폼 토글
 */
function toggleReplyForm(parentId) {
    const replyForm = document.getElementById('reply-form-' + parentId);
    if (replyForm) {
        if (replyForm.style.display === 'none' || replyForm.style.display === '') {
            replyForm.style.display = 'block';
            const textarea = document.getElementById('reply-content-' + parentId);
            if (textarea) {
                textarea.focus();
            }
        } else {
            replyForm.style.display = 'none';
        }
    }
}

/**
 * 대댓글 작성 취소
 */
function cancelReply(parentId) {
    const replyForm = document.getElementById('reply-form-' + parentId);
    if (replyForm) {
        replyForm.style.display = 'none';
        const textarea = document.getElementById('reply-content-' + parentId);
        if (textarea) {
            textarea.value = '';
        }
    }
}

/**
 * 대댓글 작성
 */
async function createReply(parentId) {
    const textarea = document.getElementById('reply-content-' + parentId);
    if (!textarea) {
        return;
    }
    
    const content = textarea.value.trim();
    if (!content) {
        alert('답글 내용을 입력하세요.');
        return;
    }
    
    try {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        const response = await fetch(`/comment/${parentId}/reply`, {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin',
            body: JSON.stringify({ content: content })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 대댓글 폼 숨기기
            cancelReply(parentId);
            
            // 대댓글 목록에 추가
            addReplyToUI(parentId, data.comment);
            
            // 댓글 수 업데이트 (DOM에서 재계산)
            updateCommentCountFromDOM();
        } else {
            alert(data.error || '답글 작성 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('답글 작성 오류:', error);
        alert('답글 작성 중 오류가 발생했습니다.');
    }
}

/**
 * 대댓글을 UI에 추가
 */
function addReplyToUI(parentId, replyData) {
    const repliesList = document.getElementById('replies-' + parentId);
    if (!repliesList) {
        // 대댓글 목록이 없으면 생성
        const commentItem = document.querySelector(`[data-comment-id="${parentId}"]`);
        if (commentItem) {
            const commentContent = commentItem.querySelector('.comment-content');
            if (commentContent) {
                const newRepliesList = document.createElement('div');
                newRepliesList.className = 'replies-list';
                newRepliesList.id = 'replies-' + parentId;
                commentContent.appendChild(newRepliesList);
            }
        }
    }
    
    const repliesContainer = document.getElementById('replies-' + parentId);
    if (!repliesContainer) {
        return;
    }
    
    // 대댓글 HTML 생성
    const replyItem = document.createElement('div');
    replyItem.className = 'reply-item';
    replyItem.setAttribute('data-comment-id', replyData.id);
    
    const avatarPlaceholder = (replyData.nickname || replyData.username || 'U')[0];
    const createdAt = new Date(replyData.created_at).toLocaleString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // 현재 사용자 ID 확인 (페이지에서 가져오거나 전역 변수 사용)
    const currentUserId = window.currentUserId || null;
    
    replyItem.innerHTML = `
        <div class="reply-avatar">
            <div class="comment-avatar-placeholder">${avatarPlaceholder}</div>
        </div>
        <div class="reply-content">
            <div class="reply-header">
                <span class="reply-author">${escapeHtml(replyData.nickname || replyData.username || '사용자')}</span>
                <span class="reply-date">${createdAt}</span>
            </div>
            <div class="reply-text">${escapeHtml(replyData.content)}</div>
            ${currentUserId && currentUserId === replyData.user_id ? `
            <div class="reply-actions">
                <button class="comment-action-btn edit" 
                        data-comment-id="${replyData.id}" 
                        data-comment-content="${escapeHtml(replyData.content)}"
                        onclick="editCommentFromButton(this)">수정</button>
                <button class="comment-action-btn delete" 
                        onclick="deleteComment(${replyData.id})">삭제</button>
            </div>
            <div id="edit-form-${replyData.id}" class="comment-edit-form" style="display: none;">
                <textarea id="edit-content-${replyData.id}" required>${escapeHtml(replyData.content)}</textarea>
                <div class="comment-edit-actions">
                    <button type="button" class="btn btn-primary btn-sm" onclick="updateComment(${replyData.id})">저장</button>
                    <button type="button" class="btn btn-secondary btn-sm" onclick="cancelEdit(${replyData.id})">취소</button>
                </div>
            </div>
            ` : ''}
        </div>
    `;
    
    repliesContainer.appendChild(replyItem);
}

/**
 * HTML 이스케이프 헬퍼 함수
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 댓글 좋아요 토글
 */
async function toggleCommentLike(commentId) {
    const likeBtn = document.querySelector(`[data-comment-id="${commentId}"].comment-like-btn`);
    const dislikeBtn = document.querySelector(`[data-comment-id="${commentId}"].comment-dislike-btn`);
    const likeCount = document.getElementById(`comment-like-count-${commentId}`);
    const dislikeCount = document.getElementById(`comment-dislike-count-${commentId}`);
    
    if (!likeBtn || likeBtn.classList.contains('disabled')) {
        return;
    }
    
    // 버튼 비활성화 (중복 클릭 방지)
    likeBtn.disabled = true;
    if (dislikeBtn) dislikeBtn.disabled = true;
    
    try {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        const response = await fetch(`/comment/${commentId}/like`, {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 좋아요 상태 업데이트
            if (data.is_liked) {
                likeBtn.classList.add('liked');
            } else {
                likeBtn.classList.remove('liked');
            }
            
            // 싫어요는 항상 취소됨
            if (dislikeBtn) {
                dislikeBtn.classList.remove('disliked');
            }
            
            // 개수 업데이트
            if (likeCount) {
                likeCount.textContent = data.likes_count || 0;
            }
            if (dislikeCount && data.dislikes_count !== undefined) {
                dislikeCount.textContent = data.dislikes_count || 0;
            }
        } else {
            alert('좋아요 처리 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('댓글 좋아요 오류:', error);
        alert('좋아요 처리 중 오류가 발생했습니다.');
    } finally {
        // 버튼 다시 활성화
        likeBtn.disabled = false;
        if (dislikeBtn) dislikeBtn.disabled = false;
    }
}

/**
 * 댓글 싫어요 토글
 */
async function toggleCommentDislike(commentId) {
    const likeBtn = document.querySelector(`[data-comment-id="${commentId}"].comment-like-btn`);
    const dislikeBtn = document.querySelector(`[data-comment-id="${commentId}"].comment-dislike-btn`);
    const likeCount = document.getElementById(`comment-like-count-${commentId}`);
    const dislikeCount = document.getElementById(`comment-dislike-count-${commentId}`);
    
    if (!dislikeBtn || dislikeBtn.classList.contains('disabled')) {
        return;
    }
    
    // 버튼 비활성화 (중복 클릭 방지)
    dislikeBtn.disabled = true;
    if (likeBtn) likeBtn.disabled = true;
    
    try {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        const response = await fetch(`/comment/${commentId}/dislike`, {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 싫어요 상태 업데이트
            if (data.is_disliked) {
                dislikeBtn.classList.add('disliked');
            } else {
                dislikeBtn.classList.remove('disliked');
            }
            
            // 좋아요는 항상 취소됨
            if (likeBtn) {
                likeBtn.classList.remove('liked');
            }
            
            // 개수 업데이트
            if (dislikeCount) {
                dislikeCount.textContent = data.dislikes_count || 0;
            }
            if (likeCount && data.likes_count !== undefined) {
                likeCount.textContent = data.likes_count || 0;
            }
        } else {
            alert('싫어요 처리 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('댓글 싫어요 오류:', error);
        alert('싫어요 처리 중 오류가 발생했습니다.');
    } finally {
        // 버튼 다시 활성화
        dislikeBtn.disabled = false;
        if (likeBtn) likeBtn.disabled = false;
    }
}

/**
 * 좋아요 토글
 */
async function toggleLike(videoId) {
    const likeBtn = document.getElementById('like-btn');
    const likeCount = document.getElementById('like-count');
    
    if (!likeBtn || likeBtn.classList.contains('disabled')) {
        return;
    }
    
    // 버튼 비활성화 (중복 클릭 방지)
    likeBtn.disabled = true;
    
    try {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        const response = await fetch(`/video/${videoId}/like`, {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 좋아요 상태 업데이트
            if (data.is_liked) {
                likeBtn.classList.add('liked');
            } else {
                likeBtn.classList.remove('liked');
            }
            
            // 좋아요 개수 업데이트
            if (likeCount) {
                likeCount.textContent = data.likes_count;
            }
        } else {
            alert('좋아요 처리 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('좋아요 오류:', error);
        alert('좋아요 처리 중 오류가 발생했습니다.');
    } finally {
        // 버튼 다시 활성화
        likeBtn.disabled = false;
    }
}

/**
 * 구독 토글
 */
async function toggleSubscribe(userId) {
    const subscribeBtn = document.getElementById('subscribe-btn');
    const subscribeText = document.getElementById('subscribe-text');
    const subscriberCount = document.getElementById('subscriber-count');
    
    if (!subscribeBtn || subscribeBtn.classList.contains('disabled')) {
        return;
    }
    
    // 버튼 비활성화 (중복 클릭 방지)
    subscribeBtn.disabled = true;
    
    try {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        const response = await fetch(`/user/${userId}/subscribe`, {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 구독 상태 업데이트
            if (data.is_subscribed) {
                subscribeBtn.classList.add('subscribed');
                subscribeText.textContent = '구독 취소';
            } else {
                subscribeBtn.classList.remove('subscribed');
                subscribeText.textContent = '구독';
            }
            
            // 구독자 수 업데이트
            if (subscriberCount) {
                subscriberCount.textContent = data.subscriber_count.toLocaleString();
            }
        } else {
            alert(data.error || '구독 처리 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('구독 오류:', error);
        alert('구독 처리 중 오류가 발생했습니다.');
    } finally {
        // 버튼 다시 활성화
        subscribeBtn.disabled = false;
    }
}

/**
 * 댓글 목록 로드 (API)
 */
async function loadComments(videoId) {
    try {
        const response = await fetch(`/api/videos/${videoId}/comments`);
        const result = await response.json();
        
        if (result.success) {
            renderComments(result.data.comments);
            updateCommentCount(result.data.count);
        }
    } catch (error) {
        console.error('댓글 로드 오류:', error);
    }
}

/**
 * 댓글 렌더링
 */
function renderComments(comments) {
    const commentsList = document.getElementById('comments-list');
    if (!commentsList) return;
    
    if (comments.length === 0) {
        commentsList.innerHTML = '<div class="comments-empty"><p>아직 댓글이 없습니다. 첫 번째 댓글을 작성해보세요!</p></div>';
        return;
    }
    
    commentsList.innerHTML = comments.map(comment => `
        <div class="comment-item" data-comment-id="${comment.id}">
            <div class="comment-avatar">
                ${comment.author.profile_image 
                    ? `<img src="/uploads/profile_images/${comment.author.profile_image}" alt="프로필">`
                    : `<div class="comment-avatar-placeholder">${(comment.author.nickname || comment.author.username)[0]}</div>`
                }
            </div>
            <div class="comment-content">
                <div class="comment-header">
                    <span class="comment-author">${comment.author.nickname || comment.author.username}</span>
                    <span class="comment-date">${formatDate(comment.created_at)}</span>
                    ${comment.updated_at !== comment.created_at ? '<span class="comment-date">(수정됨)</span>' : ''}
                </div>
                <div class="comment-text">${escapeHtml(comment.content)}</div>
                ${comment.is_author ? `
                    <div class="comment-actions">
                        <button class="comment-action-btn edit" 
                                data-comment-id="${comment.id}" 
                                data-comment-content="${escapeHtml(comment.content)}"
                                onclick="editCommentFromButton(this)">수정</button>
                        <button class="comment-action-btn delete" 
                                onclick="deleteComment(${comment.id})">삭제</button>
                    </div>
                    <div id="edit-form-${comment.id}" class="comment-edit-form" style="display: none;">
                        <textarea id="edit-content-${comment.id}" required>${escapeHtml(comment.content)}</textarea>
                        <div class="comment-edit-actions">
                            <button type="button" class="btn btn-primary btn-sm" onclick="updateComment(${comment.id})">저장</button>
                            <button type="button" class="btn btn-secondary btn-sm" onclick="cancelEdit(${comment.id})">취소</button>
                        </div>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

/**
 * 댓글 작성 (API) - 폼 기반으로 변경되어 이 함수는 더 이상 사용되지 않음
 * 대댓글 작성 등에서만 사용될 수 있음
 */
async function createComment(videoId) {
    console.warn('createComment 함수는 더 이상 사용되지 않습니다. 폼 기반 제출을 사용하세요.');
    // 폼 제출로 대체
    const form = document.getElementById('comment-form');
    if (form) {
        form.submit();
    } else {
        alert('댓글 작성 폼을 찾을 수 없습니다.');
    }
}

/**
 * 댓글 수정 (API)
 */
async function updateComment(commentId) {
    const textarea = document.getElementById(`edit-content-${commentId}`);
    const content = textarea ? textarea.value.trim() : '';
    
    if (!content) {
        alert('댓글 내용을 입력해주세요.');
        return;
    }
    
    try {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        const response = await fetch(`/api/comments/${commentId}`, {
            method: 'PUT',
            headers: headers,
            credentials: 'same-origin',
            body: JSON.stringify({ content })
        });
        
        const result = await response.json();
        
        if (result.success) {
            cancelEdit(commentId);
            // SSR 템플릿과 동일한 구조로 다시 렌더하려면 페이지 새로고침이 가장 안정적
            location.reload();
        } else {
            alert(result.error || '댓글 수정 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('댓글 수정 오류:', error);
        alert('댓글 수정 중 오류가 발생했습니다.');
    }
}

/**
 * 댓글 삭제 (API)
 */
async function deleteComment(commentId) {
    if (!confirm('댓글을 삭제하시겠습니까?')) {
        return;
    }
    
    try {
        const csrfToken = getCSRFToken();
        const headers = {};
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        const response = await fetch(`/api/comments/${commentId}`, {
            method: 'DELETE',
            headers: headers,
            credentials: 'same-origin'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 댓글 삭제 후 SSR 구조 유지를 위해 페이지 새로고침
            location.reload();
        } else {
            alert(result.error || '댓글 삭제 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('댓글 삭제 오류:', error);
        alert('댓글 삭제 중 오류가 발생했습니다.');
    }
}

/**
 * 댓글 개수 업데이트 (숫자 또는 DOM 기반)
 */
function updateCommentCount(count) {
    const countElement = document.getElementById('comment-count');
    if (countElement) {
        countElement.textContent = `${count !== undefined ? count : 0}개`;
    }
}

/**
 * DOM의 댓글/대댓글 개수로 comment-count 업데이트
 */
function updateCommentCountFromDOM() {
    const commentsList = document.getElementById('comments-list');
    const countElement = document.getElementById('comment-count');
    if (commentsList && countElement) {
        const items = commentsList.querySelectorAll('.comment-item, .reply-item');
        countElement.textContent = `${items.length}개`;
    }
}

/**
 * 날짜 포맷팅
 */
function formatDate(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    return `${date.getFullYear()}년 ${String(date.getMonth() + 1).padStart(2, '0')}월 ${String(date.getDate()).padStart(2, '0')}일 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

/**
 * HTML 이스케이프
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 다크 모드 초기화
 */
function initDarkMode() {
    // 저장된 테마 설정 불러오기
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // 다크 모드 토글 버튼 이벤트 리스너
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

/**
 * 테마 설정
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

