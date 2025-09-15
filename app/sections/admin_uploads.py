import streamlit as st
from app.components.admin import is_admin
from core.utils import upload_file, get_first_file_name

PATHS = {
    "MEDIA_CONSUMPTION": "research/media-consumption-uploads",
    "SITES_AFFINITY": "research/sites-affinity-uploads",
    "JSON": "research/json",
}

def admin_uploads():
    if st.query_params.get('mode') == 'admin' and is_admin():
        
        st.title("Admin Upload Section")
        st.markdown("---")
        
        # MEDIA CONSUMPTION
        uploaded_file_media_consumption = st.file_uploader(
                "Upload Media Consumption Research",
                key="Upload Media Consumption Research",
                type=["png"],
                help="Supported formats: PNG"
            )
        upload_media_consumption_button_handler = st.button("Replace media consumption research file", type="secondary", use_container_width=True)
        if upload_media_consumption_button_handler and uploaded_file_media_consumption:
            save_path = PATHS.get("MEDIA_CONSUMPTION")
            upload_file(uploaded_file_media_consumption, save_path)
        
        # SITES AFFINITY
        uploaded_file_sites_affinity = st.file_uploader(
                "Upload Sites Affinity Research",
                key="Upload Sites Affinity Research",
                type=["CSV"],
                help="Supported formats: CSV"
            )
        upload_sites_affinity_button_handler = st.button("Replace sites affinity research file", type="secondary", use_container_width=True)
        if upload_sites_affinity_button_handler and uploaded_file_sites_affinity:
            save_path = PATHS.get("SITES_AFFINITY")
            upload_file(uploaded_file_sites_affinity, save_path)

        # Display the uploaded files
        st.subheader("Uploaded Files")
        media_consumption_file = get_first_file_name(PATHS.get("MEDIA_CONSUMPTION"))
        if media_consumption_file:
            st.write(f"Media Consumption Research File: {media_consumption_file}")
        else:
            st.write("Media Consumption Research File: No file uploaded yet.")
        sites_affinity_file = get_first_file_name(PATHS.get("SITES_AFFINITY"))
        if sites_affinity_file:
            st.write(f"Sites Affinity Research File: {sites_affinity_file}")
        else:
            st.write("Sites Affinity Research File: No file uploaded yet.")

        # new_file_uploaded = False
        
        # print(get_corresponding_json_file(psychography_file))
        # if(psychography_file and get_corresponding_json_file(psychography_file)):
        #     new_file_uploaded = True
        # if(media_consumption_file and get_corresponding_json_file(media_consumption_file)):
        #     new_file_uploaded = True
        # if(sites_affinity_file and get_corresponding_json_file(sites_affinity_file)):
        #     new_file_uploaded = True



        # analyze_files_button_handler = st.button("Analyse Research Files", type="primary", use_container_width=True, disabled=(not new_file_uploaded))
        
        # if analyze_files_button_handler:
        #     if new_file_uploaded:
                
        #         # Perform analysis on the uploaded files
        #         st.success("Files analyzed successfully!")


# def get_corresponding_json_file(file_name):
#     # Get the corresponding JSON file name based on the uploaded file name
#     base_file_name = os.path.splitext(file_name)[0]
#     json_file_name =  f"{PATHS.get('JSON')}/{base_file_name}.json"
#     print(base_file_name)
#     print(json_file_name)
#     print(os.path.exists(json_file_name))
#     if not os.path.exists(json_file_name):
#         return True
