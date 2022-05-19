<?php
class GenreModel extends CI_Model
{
    public function __construct()
    {
        $this->load->database();
    }

    public function get_all_genres()
    {
        $query = $this->db->get('genres');
        return $query->result_array();
    }

    public function get_genre_by_id($id)
    {
        $query = $this->db->get_where('genres', ['id' => $id]);
        return $query->row_array();
    }
}
