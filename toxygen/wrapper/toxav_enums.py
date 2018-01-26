TOXAV_ERR_NEW = {
    # The function returned successfully.
    'OK': 0,
    # One of the arguments to the function was NULL when it was not expected.
    'NULL': 1,
    # Memory allocation failure while trying to allocate structures required for the A/V session.
    'MALLOC': 2,
    # Attempted to create a second session for the same Tox instance.
    'MULTIPLE': 3,
}

TOXAV_ERR_CALL = {
    # The function returned successfully.
    'OK': 0,
    # A resource allocation error occurred while trying to create the structures required for the call.
    'MALLOC': 1,
    # Synchronization error occurred.
    'SYNC': 2,
    # The friend number did not designate a valid friend.
    'FRIEND_NOT_FOUND': 3,
    # The friend was valid, but not currently connected.
    'FRIEND_NOT_CONNECTED': 4,
    # Attempted to call a friend while already in an audio or video call with them.
    'FRIEND_ALREADY_IN_CALL': 5,
    # Audio or video bit rate is invalid.
    'INVALID_BIT_RATE': 6,
}

TOXAV_ERR_ANSWER = {
    # The function returned successfully.
    'OK': 0,
    # Synchronization error occurred.
    'SYNC': 1,
    # Failed to initialize codecs for call session. Note that codec initiation will fail if there is no receive callback
    # registered for either audio or video.
    'CODEC_INITIALIZATION': 2,
    # The friend number did not designate a valid friend.
    'FRIEND_NOT_FOUND': 3,
    # The friend was valid, but they are not currently trying to initiate a call. This is also returned if this client
    # is already in a call with the friend.
    'FRIEND_NOT_CALLING': 4,
    # Audio or video bit rate is invalid.
    'INVALID_BIT_RATE': 5,
}

TOXAV_FRIEND_CALL_STATE = {
    # Set by the AV core if an error occurred on the remote end or if friend timed out. This is the final state after
    # which no more state transitions can occur for the call. This call state will never be triggered in combination
    # with other call states.
    'ERROR': 1,
    # The call has finished. This is the final state after which no more state transitions can occur for the call. This
    # call state will never be triggered in combination with other call states.
    'FINISHED': 2,
    # The flag that marks that friend is sending audio.
    'SENDING_A': 4,
    # The flag that marks that friend is sending video.
    'SENDING_V': 8,
    # The flag that marks that friend is receiving audio.
    'ACCEPTING_A': 16,
    # The flag that marks that friend is receiving video.
    'ACCEPTING_V': 32,
}

TOXAV_CALL_CONTROL = {
    # Resume a previously paused call. Only valid if the pause was caused by this client, if not, this control is
    # ignored. Not valid before the call is accepted.
    'RESUME': 0,
    # Put a call on hold. Not valid before the call is accepted.
    'PAUSE': 1,
    # Reject a call if it was not answered, yet. Cancel a call after it was answered.
    'CANCEL': 2,
    # Request that the friend stops sending audio. Regardless of the friend's compliance, this will cause the
    # audio_receive_frame event to stop being triggered on receiving an audio frame from the friend.
    'MUTE_AUDIO': 3,
    # Calling this control will notify client to start sending audio again.
    'UNMUTE_AUDIO': 4,
    # Request that the friend stops sending video. Regardless of the friend's compliance, this will cause the
    # video_receive_frame event to stop being triggered on receiving a video frame from the friend.
    'HIDE_VIDEO': 5,
    # Calling this control will notify client to start sending video again.
    'SHOW_VIDEO': 6,
}

TOXAV_ERR_CALL_CONTROL = {
    # The function returned successfully.
    'OK': 0,
    # Synchronization error occurred.
    'SYNC': 1,
    # The friend_number passed did not designate a valid friend.
    'FRIEND_NOT_FOUND': 2,
    # This client is currently not in a call with the friend. Before the call is answered, only CANCEL is a valid
    # control.
    'FRIEND_NOT_IN_CALL': 3,
    # Happens if user tried to pause an already paused call or if trying to resume a call that is not paused.
    'INVALID_TRANSITION': 4,
}

TOXAV_ERR_BIT_RATE_SET = {
    # The function returned successfully.
    'OK': 0,
    # Synchronization error occurred.
    'SYNC': 1,
    # The audio bit rate passed was not one of the supported values.
    'INVALID_AUDIO_BIT_RATE': 2,
    # The video bit rate passed was not one of the supported values.
    'INVALID_VIDEO_BIT_RATE': 3,
    # The friend_number passed did not designate a valid friend.
    'FRIEND_NOT_FOUND': 4,
    # This client is currently not in a call with the friend.
    'FRIEND_NOT_IN_CALL': 5,
}

TOXAV_ERR_SEND_FRAME = {
    # The function returned successfully.
    'OK': 0,
    # In case of video, one of Y, U, or V was NULL. In case of audio, the samples data pointer was NULL.
    'NULL': 1,
    # The friend_number passed did not designate a valid friend.
    'FRIEND_NOT_FOUND': 2,
    # This client is currently not in a call with the friend.
    'FRIEND_NOT_IN_CALL': 3,
    # Synchronization error occurred.
    'SYNC': 4,
    # One of the frame parameters was invalid. E.g. the resolution may be too small or too large, or the audio sampling
    # rate may be unsupported.
    'INVALID': 5,
    # Either friend turned off audio or video receiving or we turned off sending for the said payload.
    'PAYLOAD_TYPE_DISABLED': 6,
    # Failed to push frame through rtp interface.
    'RTP_FAILED': 7,
}
